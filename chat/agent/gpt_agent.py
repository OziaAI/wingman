from openai import OpenAI
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionMessageParam,
    ChatCompletionMessageToolCall,
)
from chat.agent.agent_tools import ToolParam

from .message import (
    UserMessageAction,
    WingmanMessage,
    WingmanMessageContext,
    WingmanMessageOption,
)
from .agent_tools import ToolManager, tool


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
        print(self.tools)

    def create_prompt(self) -> ChatCompletion:
        return self.client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
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
        satisfaction_text: str,
        satisfaction_button: str,
        dissatisfaction_text: str,
        dissatisfaction_button: str,
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
            print("Tool with name: " + fun.__name__ + " has been called")
            print(args)
            fun(self, **args)

            msg = {
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": fun.__name__,
                "content": "",
            }
            self.chats.append(msg)

        prompt = self.create_prompt()
        self.chats.append(prompt.choices[0].message)
        return prompt.choices[0].message.content

    def generate_response(self, question: str) -> WingmanMessage | None:
        self.chats.append({"role": "user", "content": question})

        message = self.create_prompt()

        answer: str | None = message.choices[0].message.content
        answer = answer if answer is not None else ""

        self.chats.append(message.choices[0].message)

        new_answer = self.execute_tool_calls(message.choices[0].message.tool_calls)
        answer = new_answer if new_answer is not None else answer

        # Option reset so that future response generation are not affected by previous option generation
        options = self.options
        self.options = None

        return WingmanMessage(
            message=answer if answer is not None else "",
            context=self.context,
            option=options,
        )
