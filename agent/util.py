import json


def check_for_agent_restart(conversation) -> bool:
    agent_initiated_restart = False
    # Check if the last tool result indicates an agent-initiated restart
    for i in range(len(conversation) - 1, -1, -1):
        msg = conversation[i]
        if msg["role"] == "user" and "content" in msg and isinstance(msg["content"], list):
            for item in msg["content"]:
                if item.get("type") == "tool_result" and isinstance(item.get("content"), str):
                    try:
                        tool_result = json.loads(item["content"])
                        if isinstance(tool_result, dict) and tool_result.get("restart") and tool_result.get(
                                "agent_initiated"):
                            agent_initiated_restart = True
                            print("Continuing execution after agent-initiated restart")
                            break
                    except (json.JSONDecodeError, TypeError):
                        pass
        if agent_initiated_restart:
            break

    return agent_initiated_restart


def log_error(error_message):
    """Log error message to error.txt file"""
    try:
        with open("error.txt", "a") as f:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"\n[{timestamp}] ERROR: {error_message}\n")
        print(f"Error logged to error.txt")
    except Exception as e:
        print(f"Failed to log error to file: {str(e)}")


def get_user_message():
    """Get user message from standard input.
    Returns a tuple of (message, success_flag)
    """
    try:
        text = input()
        return text, True
    except EOFError:
        return "", False
