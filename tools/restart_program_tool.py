# restart_program_tool.py

import json
import os
import sys
import pickle
from datetime import datetime
from tools.base_tool import ToolDefinition

# ------------------------------------------------------------------
# Input‐schema for the restart_program tool
# ------------------------------------------------------------------
RestartProgramInputSchema = {
    "type": "object",
    "properties": {
        "reason": {
            "type": "string",
            "description": "Optional reason for restarting the program"
        },
        "save_file": {
            "type": "string",
            "description": "Optional file path to save conversation context to. Defaults to 'conversation_context.pkl'"
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
    save_file = input_data.get("save_file", "conversation_context.pkl")
    
    try:
        # Get the global context object where conversation history is stored
        # The exact implementation depends on how your agent stores conversation history
        # This is a placeholder - replace with actual context access in your implementation
        from base_agent import get_conversation_context
        context = get_conversation_context()
        
        # Save conversation context to file
        with open(save_file, 'wb') as f:
            pickle.dump(context, f)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result = {
            "success": True,
            "message": f"Program will restart. Conversation saved to {save_file} at {timestamp}",
            "reason": reason
        }
        
        # This will force the program to exit and then your process manager
        # (e.g., systemd, supervisor, or a shell script) should restart it
        # You could also implement direct restart logic here depending on your setup
        
        # Schedule restart after returning result
        # We use os._exit instead of sys.exit to ensure immediate termination
        def restart_after_response():
            os._exit(42)  # Use a special exit code to signal intentional restart
            
        # Set up a timer to restart after a short delay
        import threading
        threading.Timer(1.0, restart_after_response).start()
        
        return json.dumps(result)
    except Exception as e:
        result = {
            "success": False,
            "error": str(e)
        }
        return json.dumps(result)


# ------------------------------------------------------------------
# ToolDefinition instance
# ------------------------------------------------------------------
RestartProgramDefinition = ToolDefinition(
    name="restart_program",
    description="Restart the Python program while preserving the conversation context by saving it to a file and reloading on startup",
    input_schema=RestartProgramInputSchema,
    function=restart_program
)