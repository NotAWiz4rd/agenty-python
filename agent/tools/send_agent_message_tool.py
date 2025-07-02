# send_agent_message_tool.py

import json

import requests

from team_config_loader import get_agent_endpoints
from tools.base_tool import ToolDefinition

# ------------------------------------------------------------------
# Input‐schema for the send_agent_message tool
# ------------------------------------------------------------------
SendAgentMessageInputSchema = {
    "type": "object",
    "properties": {
        "target_agent": {
            "type": "string",
            "description": "The name of the target agent to send the message to (e.g., 'agent1')."
        },
        "message": {
            "type": "string",
            "description": "The content of the message to send to the target agent."
        },
        "from_agent": {
            "type": "string",
            "description": "The name of the agent sending the message (your name)."
        }
    },
    "required": ["target_agent", "from_agent", "message"]
}

# we only need to load this once
AGENT_ENDPOINTS = None


def send_agent_message(input_data: dict) -> str:
    """
    Sends a direct message to a specific agent via their API endpoint.
    """

    # we only need to load this once
    global AGENT_ENDPOINTS
    if AGENT_ENDPOINTS is None:
        AGENT_ENDPOINTS = get_agent_endpoints()

    # Allow raw JSON string or parsed dict
    if isinstance(input_data, str):
        input_data = json.loads(input_data)

    target_agent = input_data.get("target_agent")
    message = input_data.get("message")
    from_agent = input_data.get("from_agent")

    if not target_agent or not message or not from_agent:
        return "Error: target_agent, message and from_agent are required."

    # Check if target agent exists in our endpoints
    if target_agent not in AGENT_ENDPOINTS:
        available_agents = ", ".join(AGENT_ENDPOINTS.keys())
        return f"Unknown target agent '{target_agent}'. Available agents: {available_agents}"

    # Get the API endpoint for the target agent
    api_url = AGENT_ENDPOINTS[target_agent] + "/send-message"

    payload = {"message": message, "from_agent": from_agent}

    try:
        response = requests.post(api_url, json=payload, timeout=5)
        response.raise_for_status()
        return f"Message sent to {target_agent}: {message}"
    except requests.ConnectionError:
        return f"Failed to connect to {target_agent} at {api_url}. Agent may be offline."
    except requests.RequestException as e:
        return f"Failed to send message to {target_agent}: {e}"


# ------------------------------------------------------------------
# ToolDefinition instance
# ------------------------------------------------------------------
SendAgentMessageDefinition = ToolDefinition(
    name="send_agent_message",
    description=(
        "Send a direct message to a specific agent in your team. "
        "This allows private communication between agents rather than broadcasting to the group. "
        "Specify the target agent name and your message content."
    ),
    input_schema=SendAgentMessageInputSchema,
    function=send_agent_message
)
