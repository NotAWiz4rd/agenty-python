# send_group_message_tool.py

import json

import requests

from agent.tools.base_tool import ToolDefinition

# ------------------------------------------------------------------
# Input‐schema for the send_group_message tool
# ------------------------------------------------------------------
SendGroupMessageInputSchema = {
    "type": "object",
    "properties": {
        "username": {
            "type": "string",
            "description": "The username to send as."
        },
        "message": {
            "type": "string",
            "description": "The content of the message to send to the group chat."
        }
    },
    "required": ["username", "message"]
}

API_URL = "http://127.0.0.1:5000/send"


def send_group_message(input_data: dict) -> str:
    """
    Sends a message to the group chat via the API.
    """
    # Allow raw JSON string or parsed dict
    if isinstance(input_data, str):
        input_data = json.loads(input_data)

    username = input_data.get("username")  # todo force agent to use its own username
    message = input_data.get("message")

    if not username or not message:
        return "Username and message are required."

    payload = {"username": username, "message": message}
    try:
        response = requests.post(API_URL, json=payload, timeout=5)
        response.raise_for_status()
        return f"Message sent as '{username}': {message}"
    except requests.RequestException as e:
        return f"Failed to send message: {e}"


# ------------------------------------------------------------------
# ToolDefinition instance
# ------------------------------------------------------------------
SendGroupMessageDefinition = ToolDefinition(
    name="send_group_message",
    description=(
        "Send a message to the group chat of your team of agents. "
        "You cannot read or retrieve messages with this tool."
    ),
    input_schema=SendGroupMessageInputSchema,
    function=send_group_message
)
