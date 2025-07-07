import time

from tools.base_tool import ToolDefinition

# ------------------------------------------------------------------
# Input-schema for the wait tool
# ------------------------------------------------------------------
WaitInputSchema = {
    "type": "object",
    "properties": {
        "seconds": {
            "type": "number",
            "minimum": 0,
            "description": "The number of seconds to wait."
        }
    },
    "required": ["seconds"]
}


def wait(input_data: dict) -> str:
    """
    Pauses execution for the specified number of seconds.
    """
    seconds = input_data.get("seconds", 0)
    if not isinstance(seconds, (int, float)) or seconds < 0:
        raise ValueError("Invalid value for 'seconds'. Must be a non-negative number.")

    time.sleep(seconds)
    return f"Waited for {seconds} seconds."


# ------------------------------------------------------------------
# ToolDefinition instance
# ------------------------------------------------------------------
WaitDefinition = ToolDefinition(
    name="wait",
    description=(
        "Pause execution for a given number of seconds to wait for something to happen (e.g. expecting an answer to a message).\n"
        "Takes a non-negative number as input ('seconds')."
    ),
    input_schema=WaitInputSchema,
    function=wait
)
