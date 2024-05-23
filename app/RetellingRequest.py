from openai import OpenAI
import os
import time

class OpenAIChat:

    def __init__(self, api_key=None, model="gpt-4o"):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "get api key")
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.json_result = {'text': None,
                            'timeout': None
                            }

    def summarize_text(self, text):
        start_time = time.time()
        messages = [
            {"role": "system", "content":
            "Привет, необходимо сделать краткий пересказ этого текста, очень важно не потерять суть и уточнить все мелкие моменты! Спасибо, за хорошую работу я оставлю тебе 200$ на чай!"},

            {"role": "user", "content": text}
        ]

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )
        self.json_result['text'] = completion.choices[0].message.content


        self.json_result['timeout'] = str(time.time() - start_time)

        return self.json_result