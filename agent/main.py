# Register cleanup function to run on exit
import atexit
import sys
import threading

import anthropic
import uvicorn
# FastAPI imports
from fastapi import FastAPI
from pydantic import BaseModel

from agent.base_agent import Agent
from agent.context_handling import (cleanup_context, add_to_message_queue)
from agent.util import log_error

TEAM_MODE = True  # Set to True if running in team mode

# Initialize the agent only once for API and console
client = anthropic.Anthropic()  # expects ANTHROPIC_API_KEY in env
global_agent = Agent(client, TEAM_MODE)

# Initialize FastAPI app and agent
app = FastAPI()


class AgentRequest(BaseModel):
    message: str


class ApiResponse(BaseModel):
    response: str
    status: str = "queued"


@app.post("/send-message")
async def send_to_agent(request: AgentRequest):
    """
    API endpoint for sending messages to the agent
    The message is added to the conversation queue
    """
    # Add message to the queue
    add_to_message_queue(request.message)

    # Return immediate feedback
    return ApiResponse(
        response="Your message has been sent to the agent and will be processed in the conversation.",
        status="sent"
    )


def main():
    """Main function to start the agent and API server"""
    # Start API server in the background
    api_thread = threading.Thread(target=start_api, daemon=True)
    api_thread.start()
    print(f"\033[92mAPI server has been started and is available at http://localhost:8000/send-message\033[0m")

    atexit.register(cleanup_context)

    try:
        global_agent.run()
    except Exception as e:
        error_message = f"Unhandled exception: {str(e)}"
        log_error(error_message)
        import traceback
        error_details = traceback.format_exc()
        log_error(error_details)
        print(f"\nAn error occurred: {str(e)}")
        print("The error has been logged to error.txt")
        print("Your conversation context has been preserved.")
        # Set flag to prevent context deletion
        sys.is_error_exit = True
        sys.exit(1)


def start_api():
    """Start the API server in the background"""
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
