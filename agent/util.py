import json
import os
import pickle
import sys

import requests

GROUP_CHAT_API = "http://localhost:5000/messages"


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


def save_conversation(conversation, save_file: str):
    """Save the conversation context to a file"""
    try:
        with open(save_file, 'wb') as f:
            pickle.dump(conversation, f)
        return True
    except Exception as e:
        error_message = f"Error saving conversation: {str(e)}"
        print(error_message)
        try:
            with open("error.txt", "a") as f:
                import datetime
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"\n[{timestamp}] ERROR: {error_message}\n")
        except Exception:
            pass  # Silently fail if we can't log to error.txt
        return False


def save_conv_and_restart(conversation, save_file: str = "conversation_context.pkl"):
    save_conversation(conversation, save_file)

    # Set a flag to indicate we're intentionally restarting
    sys.is_restarting = True  # type: ignore

    # re-exec in-place:
    python = sys.executable
    os.execv(python, [python] + sys.argv)


def get_new_messages_from_group_chat(current_messages: list) -> list:
    """Get messages from the group chat"""
    try:
        # Get messages from the API endpoint
        response = requests.get(GROUP_CHAT_API)
        if response.status_code != 200:
            print(f"\033[91mFailed to fetch messages: {response.status_code}\033[0m")
            return []

        all_messages = response.json()

        # Check which messages are new
        new_messages = [message for message in all_messages if message not in current_messages]

        if not new_messages:
            return []
        else:
            print(f"\033[96mFound {len(new_messages)} new group messages\033[0m")
            return new_messages
    except Exception:
        # Silently fail to avoid disrupting the agent's normal operation
        pass
    return [] # fallback if API call fails
