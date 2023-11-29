import json

from channels.generic.websocket import WebsocketConsumer
from .agent import GptAgent

class ChatConsumer(WebsocketConsumer):
    def connect(self) -> None:
        self.accept()
        self.agent : GptAgent = GptAgent("You are a virtual shopping assistant bot.\
                                         You can only respond to questions \
                                         relating to a blue helmet or a red shirt.")
    
    def disconnect(self, code) -> None:
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        answer = self.agent.generate_response(message)
        print("Received: " + message)
        print("Answered: " + answer)
        self.send(text_data=json.dumps({"message": answer}))
