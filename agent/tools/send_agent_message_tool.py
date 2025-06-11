# send_agent_message_tool.py

import json

import requests

from agent.tools.base_tool import ToolDefinition
from agent.team_config_loader import _get_cached_team_config

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
    "required": ["target_agent", "message"]
}

# Dynamic function to get agent endpoints from team-config.json
def get_agent_endpoints():
    """
    Get agent endpoints dynamically from team-config.json
    """
    team_config = _get_cached_team_config()
    endpoints = {}

    for agent in team_config.agents:
        endpoint = f"{agent.host}:{agent.port}/send-message"
        endpoints[agent.name] = endpoint

    return endpoints


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

    if not target_agent or not message:
        return "target_agent and message are required."

    # Get the current agent's name if from_agent is not provided
    if not from_agent:
        from agent.team_config_loader import get_current_agent_name
        from_agent = get_current_agent_name() or "DefaultAgent"

    # Get dynamic endpoints from team configuration
    agent_endpoints = get_agent_endpoints()

    # Check if target agent exists in our endpoints
    if target_agent not in agent_endpoints:
        available_agents = ", ".join(agent_endpoints.keys())
        return f"Unknown target agent '{target_agent}'. Available agents: {available_agents}"

    # Get the API endpoint for the target agent
    api_url = agent_endpoints[target_agent]

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
