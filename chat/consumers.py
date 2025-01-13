import json

from channels.generic.websocket import WebsocketConsumer
from .agent import GptAgent


class ChatConsumer(WebsocketConsumer):
    def connect(self) -> None:
        self.accept()
        self.agent: GptAgent = GptAgent(
            "You are a virtual shopping assistant bot called Wingman."
            + "You can only respond to questions relating to a blue helmet or a red shirt."
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
