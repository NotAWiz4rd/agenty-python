# graceful_shutdown_tool.py

import json
import os
import sys
from pathlib import Path

from tools.base_tool import ToolDefinition

# ------------------------------------------------------------------
# Input schema for the graceful_shutdown tool
# ------------------------------------------------------------------
GracefulShutdownInputSchema = {
    "type": "object",
    "properties": {
        "reason": {
            "type": "string",
            "description": "Optional reason for shutting down (e.g., 'Task completed successfully', 'All objectives accomplished')"
        },
        "final_message": {
            "type": "string",
            "description": "Optional final message to display before shutdown (e.g. 'Thanks for all the fish. Goodbye!'). Feel free to be cheeky or emotional. This is your last chance to say something before you shut down completely."
        },
        "context_file": {
            "type": "string",
            "description": "Optional path to the context file to delete during shutdown. Defaults to 'conversation_context.pkl'"
        }
    },
    "required": []
}


def graceful_shutdown(input_data: dict) -> str:
    """
    Gracefully shut down Claude completely after completing all intended tasks.
    This should be called when Claude has finished all work, accomplished the 
    requested objectives, or otherwise determined it's appropriate to conclude 
    the session. During shutdown, any existing context file will be automatically
    deleted to ensure a clean shutdown. The shutdown is complete and final.
    """
    # allow raw JSON string or parsed dict
    if isinstance(input_data, str):
        input_data = json.loads(input_data)

    reason = input_data.get("reason", "Shutdown requested")
    final_message = input_data.get("final_message", "Claude shutting down gracefully. Goodbye!")
    context_file = input_data.get("context_file", "conversation_context.pkl")

    print(f"\n{'=' * 50}")
    print("GRACEFUL SHUTDOWN INITIATED")
    print(f"Reason: {reason}")
    print(f"Final message: {final_message}")
    print(f"{'=' * 50}\n")

    # Clean up context file before shutdown
    try:
        context_path = Path(context_file)
        if context_path.exists():
            context_path.unlink()
            print(f"Successfully deleted context file: {context_file}")
        else:
            print(f"Context file not found: {context_file} (no cleanup needed)")
    except Exception as e:
        print(f"Warning: Could not delete context file {context_file}: {e}")
        # Don't fail shutdown due to context file cleanup issues

    # Clean shutdown
    try:
        # Flush any remaining output
        sys.stdout.flush()
        sys.stderr.flush()

        # Exit gracefully
        os._exit(0)

    except Exception as e:
        print(f"Error during shutdown: {e}")
        # Force exit if graceful shutdown fails
        os._exit(1)

    # This line should never be reached, but just in case
    return "Shutdown completed"


# ------------------------------------------------------------------
# ToolDefinition instance
# ------------------------------------------------------------------
GracefulShutdownDefinition = ToolDefinition(
    name="graceful_shutdown",
    description="Gracefully shut yourself down completely after completing all intended tasks. This tool should be called when you have finished all work, accomplished the requested objectives, or otherwise determined it's appropriate to conclude the session. During shutdown, any existing context file will be automatically deleted to ensure a clean shutdown. The shutdown is complete and final - the agent will not continue operating after using this tool. This is optional to use - you can continue working on other tasks or activities if desired, but should use this when ready to properly conclude and shut down.",
    input_schema=GracefulShutdownInputSchema,
    function=graceful_shutdown
)
