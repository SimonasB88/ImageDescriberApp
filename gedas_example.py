import requests
from datetime import datetime

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Chat(BaseModel):
    message: str

@app.get("/health")
def get_health():
    return {"status": "OK"}

chat_history = {
    # "chat123": [
    #     {
    #         "role": "user",
    #         "content": "Hello, AI...",
    #         "timestamp": 1723047950
    #     },
    #     {
    #         "role": "assistant",
    #         "content": "Hello, how can I help you?"
    #         "timestamp": 1723047950
    #     }
    # ]
}

@app.post("/chat/{chat_id}")
def chat(chat_id, chat: Chat):
    if chat_id not in chat_history:
        chat_history[chat_id] = []

    chat_history[chat_id].append({
        "role": "user",
        "content": chat.message,
        "timestamp": int(datetime.now().timestamp())
    })

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        'Authorization': "Bearer ..."
    }
    body = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            *chat_history[chat_id],
            {
                "role": "user",
                "content": chat.message
            },
        ]
    }

    response = requests.post(
        url,
        headers=headers,
        json=body
    )
    response_data = response.json()

    completion_content = response_data.get("choices")[0].get("message").get("content")

    chat_history[chat_id].append({
        "role": "assistant",
        "content": completion_content,
        "timestamp": response_data.get("created")
    })

    return {"response": completion_content}

# Matches the following paths:
# /chat/chat123/history
# /chat/chat124/history
@app.get("/chat/{chat_id}/history")
def get_chat_history(chat_id: str):
    return chat_history.get(chat_id, [])
 