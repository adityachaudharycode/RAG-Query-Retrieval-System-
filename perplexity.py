# import requests

# url = "https://api.perplexity.ai/chat/completions"
# headers = {
#     "Content-Type": "application/json",
#     "Authorization": "Bearer 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"
# }
# data = {
#     "model": "sonar-large-chat",
#     "messages": [
#         {"role": "user", "content": "Hello"}
#     ]
# }

# response = requests.post(url, headers=headers, json=data)

# print("Status Code:", response.status_code)
# print("Response:", response.json())
import requests

url = "https://api.perplexity.ai/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer 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"
}

for model in ["sonar"]:
    data = {
        "model": model,
        "messages": [{"role": "user", "content": "Hello"}]
    }
    resp = requests.post(url, headers=headers, json=data)
    print(f"{model} → {resp.status_code}: {resp.json()}\n")
