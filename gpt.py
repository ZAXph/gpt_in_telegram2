import requests
from config import *


class GPT:
    def __init__(self):
        self.system_content = system_content
        self.URL = GPT_LOCAL_URL
        self.HEADERS = HEADERS
        self.MAX_TOKENS = MAX_TOKEN
        self.assistant_content = assistant_content

    def gpt_processing(self, user_content, level,  subject):
        resp = requests.post(
            self.URL,
            headers=self.HEADERS,

            json={
                "messages": [
                    {"role": "system", "content": (
                        f"Ты — дружелюбный помощник в {subject}! А так же можешь поддерживать диалог! А так же ты поддерживаешь "
                        "только русский язык.")},
                    {"role": "user", "content": user_content},
                ],
                "temperature": level,
                "max_tokens": self.MAX_TOKENS,
            }
        )
        return resp

    def gpt_processing_next(self, answer, level, subject):
        resp = requests.post(
            self.URL,
            headers=self.HEADERS,

            json={
                "messages": [
                    {"role": "system", "content": (
                        f"Ты — дружелюбный помощник в {subject}! А так же можешь поддерживать диалог! А так же ты поддерживаешь "
                        "только русский язык.")},
                    {"role": "user", "content": "Продолжить"},
                    {"role": "assistant", "content": self.assistant_content + answer}
                ],
                "temperature": level,
                "max_tokens": self.MAX_TOKENS,
            }
        )
        return resp
