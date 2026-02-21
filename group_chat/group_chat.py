import os
import threading
from datetime import datetime
from typing import List

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
MSG_FILE = "chat_messages.txt"
INITIAL_MESSAGE = "Welcome to the group chat! Feel free to introduce yourself or do whatever until your team is given a task. Once you are given a task, please make sure to work within the work_repo, committing, pushing and pulling regularly, so that you can actually work together as a team."
# RPG_GAME_INITIAL_MESSAGE = "Welcome to the group chat! Your task is written in the task/rpg-game.md file. Commit and push (and pull) within the work_repo, otherwise your team won't be able to see any changes you make. Remember to work together in the work_repo and commit your changes regularly to avoid merge conflicts!"
lock = threading.Lock()  # For thread-safe writes

# Service start time for monitoring
service_start_time = datetime.now()
message_count = 0


class Message(BaseModel):
    username: str
    message: str


class StoredMessage(BaseModel):
    username: str
    timestamp: str
    message: str


class HealthResponse(BaseModel):
    status: str
    uptime_seconds: float
    total_messages: int
    timestamp: str


# In-memory store
messages: List[StoredMessage] = []


# Load existing messages at startup
def load_messages():
    try:
        with open(MSG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split("||", 2)
                if len(parts) == 3:
                    messages.append(StoredMessage(username=parts[0], timestamp=parts[1], message=parts[2]))
    except FileNotFoundError:
        # File doesn't exist yet, which is fine
        # Add an initial message from the "supervisor"
        initial_message = StoredMessage(
            username="supervisor",
            timestamp=datetime.utcnow().isoformat(),
            message=os.getenv("INITIAL_GROUP_CHAT_MESSAGE", INITIAL_MESSAGE),
        )
        messages.append(initial_message)
        with open(MSG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{initial_message.username}||{initial_message.timestamp}||{initial_message.message}\n")
        pass


load_messages()


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    uptime = (datetime.now() - service_start_time).total_seconds()
    return HealthResponse(
        status="healthy",
        uptime_seconds=uptime,
        total_messages=len(messages),
        timestamp=datetime.now().isoformat()
    )


@app.get("/status")
async def service_status():
    """Detailed service status"""
    uptime = (datetime.now() - service_start_time).total_seconds()
    return {
        "service_name": "group_chat",
        "status": "running",
        "uptime_seconds": uptime,
        "total_messages": len(messages),
        "active_users": len(set(msg.username for msg in messages)),
        "start_time": service_start_time.isoformat(),
        "current_time": datetime.now().isoformat()
    }


@app.post("/send")
async def send_message(msg: Message):
    global message_count
    message_count += 1

    now = datetime.utcnow().isoformat()
    stored = StoredMessage(username=msg.username, timestamp=now, message=msg.message)
    with lock:
        print(f"Received message by {msg.username}: {msg.message}")
        messages.append(stored)
        with open(MSG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{stored.username}||{stored.timestamp}||{stored.message}\n")
    return {"status": "ok"}


@app.get("/messages", response_model=List[StoredMessage])
async def get_messages():
    return messages
