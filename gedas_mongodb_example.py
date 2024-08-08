import requests
from datetime import datetime
from pymongo import MongoClient
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

client = MongoClient("mongodb://localhost:27017/")
db = client.chat
chat_history = db.chat_history


class Chat(BaseModel):
    message: str


@app.get("/health")
def get_health():
    return {"status": "OK"}


@app.post("/chat/{chat_id}")
def chat(chat_id, chat: Chat):
    chat_history.insert_one(
        {
            "chat_id": chat_id,
            "role": "user",
            "content": chat.message,
            "timestamp": int(datetime.now().timestamp())
        }
    )

    previous_messages = list(chat_history.find({"chat_id": chat_id}, {"_id": 0, "content": 1, "role": 1}))

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        'Authorization': "Bearer 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"
    }
    body = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            *previous_messages,
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

    chat_history.insert_one({
        "chat_id": chat_id,
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
    history = list(chat_history.find({"chat_id": chat_id}, {"_id": 0, "content": 1, "role": 1, "timestamp": 1}))
    return history

 