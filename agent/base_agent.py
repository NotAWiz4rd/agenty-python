#!/usr/bin/env python3
import json
import os
import pickle
import sys

import anthropic

from agent.tools import SendGroupMessageDefinition
from tools.ask_human_tool import AskHumanDefinition
from tools.calculator_tool import CalculatorDefinition
from tools.delete_file_tool import DeleteFileDefinition
from tools.edit_file_tool import EditFileDefinition
from tools.git_command_tool import GitCommandDefinition
from tools.list_files_tool import ListFilesDefinition
from tools.read_file_tool import ReadFileDefinition
from tools.reset_context_tool import ResetContextDefinition
from tools.restart_program_tool import RestartProgramDefinition, save_conv_and_restart

# Global conversation context
_CONVERSATION_CONTEXT = None


def get_conversation_context():
    """Function to access the global conversation context"""
    global _CONVERSATION_CONTEXT
    return _CONVERSATION_CONTEXT


def set_conversation_context(context):
    """Function to set the global conversation context"""
    global _CONVERSATION_CONTEXT
    _CONVERSATION_CONTEXT = context


class Agent:
    def __init__(self, client, get_user_message, tools):
        self.client = client
        self.get_user_message = get_user_message
        self.tools = tools
        # Initialize counter for tracking consecutive tool calls without human interaction
        self.consecutive_tool_count = 0
        # Maximum number of consecutive tool calls allowed before forcing ask_human
        self.max_consecutive_tools = 10

    def run(self):
        # Try to load saved conversation context
        conversation = self.load_conversation()

        # Check if this is a restart initiated by the agent
        agent_initiated_restart = False
        if conversation:
            print("Restored previous conversation context")
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

            # If we're continuing after a restart, add a system message to inform the agent
            if agent_initiated_restart:
                conversation.append({
                    "role": "user",
                    "content": "The program has restarted and is continuing execution automatically. Please continue from where you left off."
                })
        else:
            conversation = []

        # Set the global conversation context reference
        set_conversation_context(conversation)

        print("Chat with Claude (use 'ctrl+c' to exit)")
        read_user_input = not agent_initiated_restart

        while True:
            if read_user_input:
                # prompt for user
                try:
                    print(f"\033[94mYou\033[0m: ", end="", flush=True)
                    user_input, ok = self.get_user_message()
                except KeyboardInterrupt:
                    # Let the atexit handler take care of deleting the context file
                    print("\nExiting program.")
                    sys.exit(0)
                if not ok:
                    break
                conversation.append({"role": "user", "content": user_input})
                # Reset consecutive tool count when user provides input
                self.consecutive_tool_count = 0

            response = self.run_inference(conversation)
            tool_results = []

            # print assistant text and collect any tool calls
            for block in response.content:
                if block.type == "text":
                    print(f"\033[93mClaude\033[0m: {block.text}")
                elif block.type == "tool_use":
                    # If the tool is ask_human, reset counter before executing
                    if block.name == "ask_human":
                        self.consecutive_tool_count = 0
                    else:  # Only increment for non-ask_human tools
                        self.consecutive_tool_count += 1
                        print(f"\033[96mConsecutive tool count: {self.consecutive_tool_count}/{self.max_consecutive_tools}\033[0m")
                        
                    result = self.execute_tool(block.id, block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })

            # 2) First, append the assistant’s own message (including its tool_use blocks!)
            conversation.append({
                "role": "assistant",
                "content": [
                    # for each block Claude returned, mirror it exactly
                    {
                        "type": b.type,
                        **({
                               "text": b.text
                           } if b.type == "text" else {
                            "id": b.id,
                            "name": b.name,
                            "input": b.input
                        })
                    }
                    for b in response.content
                ]
            })

            # 3) If there were any tool calls, follow up with your tool_results as a user turn
            if tool_results:
                conversation.append({
                    "role": "user",
                    "content": tool_results
                })
                read_user_input = False

                # detect “please restart” signals
                for tr in tool_results:
                    content = tr.get("content")
                    payload = None

                    # if it's already a dict, use it directly
                    if isinstance(content, dict):
                        payload = content
                    # if it's a string, try parsing JSON
                    elif isinstance(content, str):
                        try:
                            payload = json.loads(content)
                            if not isinstance(payload, dict):
                                # not a dict, skip
                                payload = None
                                continue
                        except (json.JSONDecodeError, TypeError):
                            # not JSON, skip
                            continue
                    # otherwise skip non‐dict, non‐str
                    else:
                        continue

                    # if tool asked for restart
                    if payload is not None and payload.get("restart"):
                        # Check if this is a reset_context request (don't save context)
                        if payload.get("reset_context"):
                            # Just restart without saving
                            # Set a flag to indicate we're intentionally restarting
                            sys.is_restarting = True
                            python = sys.executable
                            os.execv(python, [python] + sys.argv)
                        else:
                            # Normal restart - save and restart
                            save_conv_and_restart(conversation)
            else:
                read_user_input = True

    def run_inference(self, conversation):
        tools_param = []
        for t in self.tools:
            tools_param.append({
                "name": t.name,
                "description": t.description,
                "input_schema": t.input_schema
            })
            
        # If we've hit our consecutive tool limit, we'll force Claude to use the ask_human tool
        tool_choice = {"type": "auto"}
        if self.consecutive_tool_count >= self.max_consecutive_tools:
            print(f"\033[93mForcing human check-in after {self.max_consecutive_tools} consecutive tool calls\033[0m")
            # Find the ask_human tool
            ask_human_tool = next((t for t in self.tools if t.name == "ask_human"), None)
            if ask_human_tool:
                # Force the use of ask_human tool
                tool_choice = {
                    "type": "tool",
                    "name": "ask_human"
                }
                # We'll reset the counter when ask_human is actually executed

        return self.client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=4000,
            messages=conversation,
            tool_choice=tool_choice,
            tools=tools_param
        )

    def execute_tool(self, id, name, input_data):
        tool_def = next((t for t in self.tools if t.name == name), None)
        if not tool_def:
            return "tool not found"
        print(f"\033[92mtool\033[0m: {name}({json.dumps(input_data)})")
        try:
            return tool_def.function(input_data)
        except Exception as e:
            return str(e)

    @staticmethod
    def load_conversation(save_file="conversation_context.pkl"):
        """Load conversation context from a file if it exists"""
        if os.path.exists(save_file):
            try:
                with open(save_file, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                print(f"Error loading conversation: {str(e)}")
        return None


def get_user_message():
    """Get user message from standard input.
    Returns a tuple of (message, success_flag)
    """
    try:
        text = input()
        return text, True
    except EOFError:
        return "", False


def cleanup_context():
    """Delete the conversation context file"""
    # Skip cleanup if we're restarting the program intentionally
    # or if we're exiting due to an error
    if getattr(sys, "is_restarting", False) or getattr(sys, "is_error_exit", False):
        if getattr(sys, "is_error_exit", False):
            print("Context preserved due to error exit.")
        return

    context_file = "conversation_context.pkl"
    if os.path.exists(context_file):
        try:
            os.remove(context_file)
            print(f"\nContext file '{context_file}' deleted.")
        except Exception as e:
            print(f"\nError deleting context file: {str(e)}")
            log_error(f"Error deleting context file: {str(e)}")


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


def main():
    client = anthropic.Anthropic()  # expects ANTHROPIC_API_KEY in env
    tools = [
        ReadFileDefinition,
        ListFilesDefinition,
        EditFileDefinition,
        DeleteFileDefinition,
        GitCommandDefinition,
        RestartProgramDefinition,
        ResetContextDefinition,
        AskHumanDefinition,
        CalculatorDefinition,
        SendGroupMessageDefinition,
    ]
    agent = Agent(client, get_user_message, tools)

    # Register cleanup function to run on exit
    import atexit
    atexit.register(cleanup_context)

    try:
        agent.run()
    except Exception as e:
        error_message = f"Unhandled exception: {str(e)}"
        log_error(error_message)
        import traceback
        error_details = traceback.format_exc()
        log_error(error_details)
        print(f"\nAn error occurred: {str(e)}")
        print("The error has been logged to error.txt")
        print("Your conversation context has been preserved.")
        # Set flag to prevent context deletion
        sys.is_error_exit = True
        sys.exit(1)


if __name__ == "__main__":
    main()
