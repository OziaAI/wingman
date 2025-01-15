from openai import OpenAI
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionMessageParam,
    ChatCompletionMessageToolCall,
)

import os
import json
import elasticsearch
from sentence_transformers import SentenceTransformer

from chat.agent.agent_tools import ToolParam

from .message import (
    UserMessageAction,
    WingmanMessage,
    WingmanMessageContext,
    WingmanMessageOption,
)
from .agent_tools import ToolManager, tool

import logging

logger = logging.getLogger(__name__)


class GptAgent:
    def __init__(self, behaviour: str):
        self.client: OpenAI = OpenAI()
        self.behaviour = behaviour
        self.chats: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": self.behaviour}
        ]
        self.options: WingmanMessageOption | None = None
        self.context: WingmanMessageContext = WingmanMessageContext(disconnect=False)
        self.tools = ToolManager.list_available_tools()

        ES_HOST = os.getenv("ES_HOST", "localhost")
        ES_PORT = os.getenv("ES_PORT", None)
        ES_API_KEY = os.getenv("ES_API_KEY", None)

        if ES_PORT is not None:
            host = f"http://{ES_HOST}:{ES_PORT}"
        else:
            host = f"https://{ES_HOST}"

        self.es_client = elasticsearch.Elasticsearch(host, api_key=ES_API_KEY)
        self.model = SentenceTransformer("quora-distilbert-multilingual")
        self.shop_url: str | None = None
        logger.info(self.tools)

    def create_prompt(self) -> ChatCompletion:
        return self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=self.chats,
            tools=self.tools,
            tool_choice="auto",
        )

    @tool(
        "Function that enables the assistant to add clickable buttons for the user"
        + "This function shall only be called when the Assistant wants to retrieve"
        + "the satisfaction rate of the user about the service provided.",
        params={
            "satisfaction_text": ToolParam(
                type="string",
                description="specifies what text will be send by the user "
                + "when he presses the satisfaction button",
            ),
            "satisfaction_button": ToolParam(
                type="string",
                description="specifies what text will be displayed "
                + "in the satisfaction button",
            ),
            "dissatisfaction_text": ToolParam(
                type="string",
                description="specifies what text will be send by the user "
                + "when the user press the dissatisfied button",
            ),
            "dissatisfaction_button": ToolParam(
                type="string",
                description="specifies what text will be displayed "
                + "in the dissatisfaction button",
            ),
        },
    )
    def add_option_buttons(
        self,
        satisfaction_text: str = "Yes",
        satisfaction_button: str = "Yes",
        dissatisfaction_text: str = "No",
        dissatisfaction_button: str = "No",
    ):
        self.options = WingmanMessageOption(
            embeddedUrl=None,
            acceptAction=UserMessageAction(
                buttonText=satisfaction_button, messageToSend=satisfaction_text
            ),
            denyAction=UserMessageAction(
                buttonText=dissatisfaction_button, messageToSend=dissatisfaction_text
            ),
        )

    @tool(
        "Function enabling the assistant to search for items in the elasticsearch database."
        + "This function shall only be called when the Assistant is required to search for items.",
        params={
            "query": ToolParam(
                type="string",
                description="A summary of the product the user is looking for.",
            )
        },
    )
    def search_content_in_elastic(self, query: str) -> str:
        print(f"query: {query}")

        embedding = self.model.encode(query, show_progress_bar=False)

        res = self.es_client.search(
            index=self.shop_url,
            knn={
                "field": "vector",
                "query_vector": embedding,
                "k": 10,
                "num_candidates": 100,
            },
        )
        result = res["hits"]["hits"]

        search_content = {}
        best_score = 0
        for r in result:
            if r["_score"] > best_score:
                best_score = r["_score"]
                search_content["title"] = r["_source"]["title"]
                search_content["description"] = r["_source"]["description"]
                if self.options is None:
                    self.options = WingmanMessageOption(
                        embeddedUrl=None, acceptAction=None, denyAction=None
                    )
                self.options["embeddedUrl"] = r["_source"]["image_link"]

        print(search_content)
        return (
            "Here is the content returned by the database query."
            + "Please, write the content as an advertisement for the user."
            + "If nothing is matching, begin your answer by 'sorry' and "
            + "ONLY TELL the client there is no product matching its "
            + "requirements, not more not less."
            + json.dumps(search_content)
        )

    @tool(
        "Disconnects from the user, ending the conversation."
        + "You must use this function when you think the conversation should be ended."
        + "You do not have to wait for the user to tell you to stop the conversation."
        + "The conversation must only be stopped if the user is SATISFIED."
    )
    def disconnect_agent(self):
        self.context["disconnect"] = True

    def execute_tool_calls(
        self, tool_calls: list[ChatCompletionMessageToolCall] | None
    ) -> str | None:
        if not tool_calls:
            return None

        tool_call: ChatCompletionMessageToolCall
        for tool_call in tool_calls:
            (fun, args) = ToolManager.get_toolkit(tool_call)
            logger.info("Tool with name: " + fun.__name__ + " has been called")
            logger.info(args)
            content = fun(self, **args)

            msg = {
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": fun.__name__,
                "content": "" if content is None else content,
            }
            self.chats.append(msg)

        prompt = self.create_prompt()
        self.chats.append(prompt.choices[0].message)
        return prompt.choices[0].message.content

    def generate_response(self, question: str, shop_url: str) -> WingmanMessage | None:
        self.shop_url = shop_url
        self.chats.append({"role": "user", "content": question})

        message = self.create_prompt()

        answer: str | None = message.choices[0].message.content
        answer = answer if answer is not None else ""

        self.chats.append(message.choices[0].message)

        new_answer = self.execute_tool_calls(message.choices[0].message.tool_calls)
        answer = new_answer if new_answer is not None else answer

        if answer.lower().startswith("sorry") and self.options is not None:
            self.options["embeddedUrl"] = None

        # Option reset so that future response generation are not affected by previous option generation
        options = self.options
        self.options = None

        return WingmanMessage(
            message=answer if answer is not None else "",
            context=self.context,
            option=options,
        )
