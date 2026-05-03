import requests


class LLMClient:
    def __init__(self, endpoint="http://localhost:8001/generate"):
        self.endpoint = endpoint

    def generate(self, prompt):
        payload = {
            "prompt": prompt,
            "max_tokens": 128
        }

        response = requests.post(self.endpoint, json=payload)
        return response.json().get("text", "")