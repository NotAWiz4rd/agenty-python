# restart_program_tool.py

import json

from tools.base_tool import ToolDefinition

# ------------------------------------------------------------------
# Input schema for the restart_program tool
# ------------------------------------------------------------------
RestartProgramInputSchema = {
    "type": "object",
    "properties": {
        "reason": {
            "type": "string",
            "description": "Optional reason for restarting the program."
        }
    }
}


def restart_program(input_data: dict) -> str:
    """
    Saves the current conversation context to a file and restarts the program.
    Returns a JSON string with the status of the operation.
    """
    # support raw JSON string or already-parsed dict
    if isinstance(input_data, str):
        input_data = json.loads(input_data)

    reason = input_data.get("reason", "Reloading tools")

    result = {
        "message": f"Program will restart.",
        "reason": reason,
        "restart": True,
        "agent_initiated": True  # Flag to indicate this restart was initiated by the agent
    }
    return json.dumps(result)


# ------------------------------------------------------------------
# ToolDefinition instance
# ------------------------------------------------------------------
RestartProgramDefinition = ToolDefinition(
    name="restart_program",
    description=(
        "Restart the Python program while preserving the conversation context "
        "by saving it to a file and reloading on startup"
    ),
    input_schema=RestartProgramInputSchema,
    function=restart_program
)
