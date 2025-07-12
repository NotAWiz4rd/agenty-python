import json
import os
import pickle
import sys

import requests

from llm import run_inference

GROUP_CHAT_API_URL = os.getenv("GROUP_CHAT_API_URL") or "http://127.0.0.1:5000"
GROUP_CHAT_MESSAGES_ENDPOINT = GROUP_CHAT_API_URL + "/messages"

WORK_LOG_BASE_URL = os.getenv("WORK_LOG_BASE_URL") or "http://127.0.0.1:8082"
GROUP_WORK_LOG_SUMMARIES_ENDPOINT = WORK_LOG_BASE_URL + "/summaries"
LAST_SUMMARY_TIMESTAMP = None


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
        response = requests.get(GROUP_CHAT_MESSAGES_ENDPOINT)
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
    return []  # fallback if API call fails


def get_new_summaries():
    """Get summaries from the group work log API"""
    global LAST_SUMMARY_TIMESTAMP
    try:
        # Get summaries from the API endpoint
        response = requests.get(GROUP_WORK_LOG_SUMMARIES_ENDPOINT, params={"after_timestamp": LAST_SUMMARY_TIMESTAMP})
        summaries = response.json()
        if summaries:
            print(f"\033[96mFound {len(summaries)} new summaries\033[0m")
            print(f"\033[93mTimestamp of last summary: {summaries[-1].get('timestamp', 'N/A')}\033[0m")
            LAST_SUMMARY_TIMESTAMP = summaries[-1].get('timestamp', LAST_SUMMARY_TIMESTAMP)
            return summaries
    except Exception:
        # Silently fail to avoid disrupting the agent's normal operation
        pass
    return []  # fallback if API call fails


def generate_restart_summary(llm_client, conversation, tools):
    """Generate a summary of what was accomplished and next steps for restart context."""

    # Create a summarization conversation
    conversation.append(
        {
            "role": "user",
            "content": "[AUTOMATED MESSAGE] Due to token restrictions we will have to restart the current conversation. "
                       "Please provide a brief summary of what you have accomplished in this conversation and what "
                       "you should do next. Keep it concise (5-7 sentences max)."
        }
    )

    try:
        # Make the LLM call to generate summary
        summary_content, _ = run_inference(conversation, llm_client, tools)
        print("SUMMARY: " + summary_content[0].text)

        # add summary content to conversation
        conversation.append({
            "role": "assistant",
            "content": summary_content
        })

    except Exception as e:
        # Fallback to simple summary if LLM call fails
        print(f"AUTO-RESTART because of token limit: LLM summary failed ({str(e)}).")
        conversation.append({
            "role": "assistant",
            "content": "AUTO-RESTART because of token limit: LLM summary failed."
        })


def get_agent_turn_delay_in_ms(number_of_agents: int = 1, ms_per_additional_agent: int = 2000) -> int:
    """Get the agent's turn delay in milliseconds based on the number of agents in the team."""
    return (number_of_agents - 1) * ms_per_additional_agent
