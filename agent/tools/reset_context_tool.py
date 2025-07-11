# reset_context_tool.py

import json
from pathlib import Path

from tools.base_tool import ToolDefinition

# ------------------------------------------------------------------
# Input schema for the reset_context tool
# ------------------------------------------------------------------
ResetContextInputSchema = {
    "type": "object",
    "properties": {}
}


def reset_context(input_data: dict) -> str:
    """
    Deletes the conversation context file and restarts the program.
    Returns a JSON string with the status of the operation.
    """
    # support raw JSON string or already-parsed dict
    if isinstance(input_data, str):
        input_data = json.loads(input_data)

    context_file = "conversation_context.pkl"
    file_path = Path(context_file)

    # Delete the context file if it exists
    if file_path.exists():
        try:
            file_path.unlink()
            message = f"Successfully deleted context file: {context_file}"
        except Exception as e:
            message = f"Error deleting context file: {str(e)}"
    else:
        message = f"Context file not found: {context_file}"

    # Return a result that signals we need to restart WITHOUT saving context
    result = {
        "message": message,
        "restart": True,
        "reset_context": True  # Special flag to indicate we don't want to save context
    }

    return json.dumps(result)


# ------------------------------------------------------------------
# ToolDefinition instance
# ------------------------------------------------------------------
ResetContextDefinition = ToolDefinition(
    name="reset_context",
    description="Reset the conversation context by deleting the saved context file and restarting the program.",
    input_schema=ResetContextInputSchema,
    function=reset_context
)
