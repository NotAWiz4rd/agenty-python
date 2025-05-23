# send_agent_message_tool.py

import json

import requests

from agent.tools.base_tool import ToolDefinition

# ------------------------------------------------------------------
# Input‐schema for the send_agent_message tool
# ------------------------------------------------------------------
SendAgentMessageInputSchema = {
    "type": "object",
    "properties": {
        "target_agent": {
            "type": "string",
            "description": "The identifier of the target agent to send the message to (e.g., 'agent1', 'agent2', 'agent3')."
        },
        "message": {
            "type": "string",
            "description": "The content of the message to send to the target agent."
        },
        "from_agent": {
            "type": "string",
            "description": "The identifier of the agent sending the message (your agent ID)."
        }
    },
    "required": ["target_agent", "message", "from_agent"]
}

# Hardcoded agent endpoints - map agent IDs to their API endpoints
AGENT_ENDPOINTS = {
    "agent1": "http://127.0.0.1:8001/send-message",
    "agent2": "http://127.0.0.1:8002/send-message",
    "agent3": "http://127.0.0.1:8003/send-message",
    "agent4": "http://127.0.0.1:8004/send-message",
    "agent5": "http://127.0.0.1:8005/send-message"
}


def send_agent_message(input_data: dict) -> str:
    """
    Sends a direct message to a specific agent via their API endpoint.
    """
    # Allow raw JSON string or parsed dict
    if isinstance(input_data, str):
        input_data = json.loads(input_data)

    target_agent = input_data.get("target_agent")
    message = input_data.get("message")
    from_agent = input_data.get("from_agent")

    if not target_agent or not message or not from_agent:
        return "target_agent, message, and from_agent are all required."

    # Check if target agent exists in our endpoints
    if target_agent not in AGENT_ENDPOINTS:
        available_agents = ", ".join(AGENT_ENDPOINTS.keys())
        return f"Unknown target agent '{target_agent}'. Available agents: {available_agents}"

    # Get the API endpoint for the target agent
    api_url = AGENT_ENDPOINTS[target_agent]

    # Format the message to include sender information

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
        "Specify the target agent ID and your message content."
    ),
    input_schema=SendAgentMessageInputSchema,
    function=send_agent_message
)
