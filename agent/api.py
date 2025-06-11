import threading

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from agent.context_handling import add_to_message_queue
from agent.team_config_loader import AgentConfig

# Initialize FastAPI app and agent
app = FastAPI()


class MessageRequest(BaseModel):
    message: str
    from_agent: str


class ApiResponse(BaseModel):
    response: str
    status: str = "queued"


@app.post("/send-message")
async def send_to_agent(request: MessageRequest):
    """
    API endpoint for sending messages to the agent
    The message is added to the conversation queue
    """
    formatted_message = f"[Direct message from {request.from_agent}]: {request.message}"
    # Add message to the queue
    add_to_message_queue(formatted_message)

    # Return immediate feedback
    return ApiResponse(
        response="Your message has been sent to the agent and will be processed in the conversation.",
        status="sent"
    )


def start_uvicorn_app(host: str, port: int):
    """Start the FastAPI app using Uvicorn server"""
    host = host or "0.0.0.0"
    port = port or 8000
    uvicorn.run(app, host=host, port=port)


def start_api(agent_config: AgentConfig):
    """Start the API server in the background"""
    api_thread = threading.Thread(target=start_uvicorn_app, args=(agent_config.host, agent_config.port), daemon=True)
    api_thread.start()
    print(f"\033[92mAPI server has been started and is available at{agent_config.host}:{agent_config.port}/\033[0m")
