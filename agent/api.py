import threading
from datetime import datetime

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from context_handling import add_to_message_queue
from team_config_loader import AgentConfig

# Initialize FastAPI app and agent
app = FastAPI()

# Global agent status tracking
agent_start_time = datetime.now()
message_count = 0


class MessageRequest(BaseModel):
    message: str
    from_agent: str


class ApiResponse(BaseModel):
    response: str
    status: str = "queued"


class HealthResponse(BaseModel):
    status: str
    uptime_seconds: float
    messages_processed: int
    timestamp: str


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    uptime = (datetime.now() - agent_start_time).total_seconds()
    return HealthResponse(
        status="healthy",
        uptime_seconds=uptime,
        messages_processed=message_count,
        timestamp=datetime.now().isoformat(),
    )


@app.get("/status")
async def agent_status():
    """Detailed agent status endpoint"""
    uptime = (datetime.now() - agent_start_time).total_seconds()
    return {
        "agent_name": "Agent",  # This could be made dynamic based on config
        "status": "running",
        "uptime_seconds": uptime,
        "messages_processed": message_count,
        "start_time": agent_start_time.isoformat(),
        "current_time": datetime.now().isoformat(),
    }


@app.post("/send-message")
async def send_to_agent(request: MessageRequest):
    """
    API endpoint for sending messages to the agent
    The message is added to the conversation queue
    """
    global message_count
    message_count += 1

    formatted_message = f"[Direct message from {request.from_agent}]: {request.message}"
    # Add message to the queue
    add_to_message_queue(formatted_message)

    # Return immediate feedback
    return ApiResponse(
        response="Your message has been sent to the agent and will be processed in the conversation.",
        status="sent",
    )


def start_uvicorn_app(host: str, port: int):
    """Start the FastAPI app using Uvicorn server"""
    uvicorn.run(app, host=host, port=port)


def start_api(agent_config: AgentConfig | None = None):
    """Start the API server in the background"""
    host = agent_config.host if agent_config else "127.0.0.1"
    port = agent_config.port if agent_config else 8081
    api_thread = threading.Thread(
        target=start_uvicorn_app, args=(host, port), daemon=True
    )
    api_thread.start()
    print(f"\033[92mAPI server has been started and is available at {host}:{port}/\033[0m")
