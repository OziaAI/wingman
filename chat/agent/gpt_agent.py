from openai import OpenAI

class GptAgent:
    def __init__(self, behaviour: str):
        self.client : OpenAI = OpenAI()
        self.behaviour = behaviour

    def generate_response(self, question: str) -> str:
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=[
                {"role": "system", "content": self.behaviour},
                {"role": "user", "content": question}
            ]
        )
        message = response.choices[0].message.content
        return message if message is not None else "" 
