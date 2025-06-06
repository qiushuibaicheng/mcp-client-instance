import requests
import json

with open("./llm_api/config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

api_key = config["api_key"]
url = config["url"]

headers = {
    'Authorization': f'Bearer {api_key}',
    'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
    'Content-Type': 'application/json'
}


class LLM:

    def __init__(self):
        self.headers = headers
        self.url = url

    def create_message(self, model: str, max_tokens: int, messages: list):
        payload = json.dumps({
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.7,
            "stream": False
        })

        response = requests.request("POST", self.url, headers=self.headers, data=payload)
        response = json.loads(response.text)["choices"][0]["message"]["content"]

        return response


if __name__ == '__main__':
    print(LLM().create_message("gpt-4o", 1000, [{
        "role": f"user",
        "content": f"你好"
    }]))
