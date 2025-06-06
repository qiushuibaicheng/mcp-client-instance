import requests
import json

url = "https://api.gpt.ge/v1/chat/completions"

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

prompt = config["prompt"]
api_key = config["api_key"]
content = config["test_content"]

payload = json.dumps({
   "model": "gpt-4o",
   "messages": [
      {
         "role": f"user",
         "content": f"你好"
      }
   ],
   "max_tokens": 4000,
   "temperature": 0.0,
   "stream": False
})
headers = {
   'Authorization': f'Bearer {api_key}',
   'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
   'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)
response = json.loads(response.text)["choices"][0]["message"]["content"]
#
# left_index = response.index("{")
# right_index = response.index("}")

# response = json.loads(response[left_index:right_index+1])

print(response)
