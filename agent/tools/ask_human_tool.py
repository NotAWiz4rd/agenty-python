# ask_human_tool.py

import json

from tools.base_tool import ToolDefinition


def get_user_message():
    """Get user message from standard input.
    Returns a tuple of (message, success_flag)
    """
    try:
        text = input()
        return text, True
    except EOFError:
        return "", False


# ------------------------------------------------------------------
# Input‐schema for the ask_human tool
# ------------------------------------------------------------------
AskHumanInputSchema = {
    "type": "object",
    "properties": {
        "question": {
            "type": "string",
            "description": "The question or information request to send to the human user."
        },
        "reason": {
            "type": "string",
            "description": "Optional explanation for why you need this information."
        },
        "agent_name": {
            "type": "string",
            "description": "The name of the agent asking the question."
        }
    },
    "required": ["question", "agent_name"],
}


def ask_human(input_data: dict) -> str:
    """
    Interrupts the current execution to ask the human user a question.
    Returns the human's response as a string.
    """
    # Allow raw JSON string or parsed dict
    if isinstance(input_data, str):
        input_data = json.loads(input_data)

    question = input_data.get("question", "")
    reason = input_data.get("reason", "")
    agent_name = input_data.get("agent_name", "Claude")

    # Format the question to include the reason if provided
    formatted_question = question
    if reason:
        formatted_question = f"{question}\n(Reason: {reason})"

    print(f"\033[94m{agent_name} is asking\033[0m: {formatted_question}")
    print(f"\033[94mYour response\033[0m: ", end="", flush=True)

    # Use the agent's function to get user input
    user_response, ok = get_user_message()

    if not ok:
        return "Human did not provide a response."

    return user_response


# ------------------------------------------------------------------
# ToolDefinition instance
# ------------------------------------------------------------------
AskHumanDefinition = ToolDefinition(
    name="ask_human",
    description=(
        "Interrupt your current process to request information or confirmation from the human user. "
        "Use this when you need clarification, additional information, or to confirm you're on the right track."
    ),
    input_schema=AskHumanInputSchema,
    function=ask_human
)
