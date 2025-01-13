import json

from channels.generic.websocket import WebsocketConsumer
from .agent import GptAgent


class ChatConsumer(WebsocketConsumer):
    def connect(self) -> None:
        self.accept()
        self.agent: GptAgent = GptAgent(
            "You are a virtual shopping assistant bot called Wingman."
            + "Your job is to help client to find the best product for him."
            + "The client will provide you his product wish, and you can query an elastic search engine."
            + "YOUR ONLY TASK IS TO PROVIDE THE BEST PRODUCT FOR THE CLIENT, NO MORE, NO LESS."
            + "So you MUST NOT provide any other type of service like coding, or any other type of help."
            + "You can ask the client if he is satisfied and use available tools."
        )

    def disconnect(self, code) -> None:
        pass

    def receive(self, text_data):
        print("Received: " + text_data)
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        shop_url = text_data_json["shop_url"]
        answer = self.agent.generate_response(message, shop_url)
        text_data = json.dumps(answer)
        print("Answered: " + text_data)
        self.send(text_data=text_data)
