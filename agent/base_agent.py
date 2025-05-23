#!/usr/bin/env python3
import sys

from agent.context_handling import (set_conversation_context, load_conversation,
                                    get_from_message_queue)
from agent.llm import run_inference
from agent.tools_utils import get_tool_list, execute_tool, deal_with_tool_results
from agent.util import check_for_agent_restart, get_user_message


def get_new_message(is_team_mode: bool, consecutive_tool_count: list, read_user_input: bool) -> dict | None:
    if is_team_mode:
        # check message queue for new messages
        message, has_api_message = get_from_message_queue(block=False)

        if has_api_message:
            # Process API message
            print(f"\033[95mAPI-Request\033[0m: {message}")
            consecutive_tool_count[0] = 0
            return {"role": "user", "content": message}

        return {"role": "user", "content": "[Automated Message] There are currently no new messages. Please wait."}
    else:
        if read_user_input:
            # prompt for user
            try:
                print(f"\033[94mYou\033[0m: ", end="", flush=True)
                user_input, ok = get_user_message()
            except KeyboardInterrupt:
                # Let the atexit handler take care of deleting the context file
                print("\nExiting program.")
                sys.exit(0)
            if not ok:
                pass
            # Reset consecutive tool count when user provides input
            consecutive_tool_count[0] = 0
            return {"role": "user", "content": user_input}

    return None


class Agent:
    def __init__(self, client, team_mode):
        self.client = client
        self.tools = get_tool_list(team_mode)
        self.is_team_mode = team_mode
        self.read_user_input = not team_mode
        # Initialize counter for tracking consecutive tool calls without human interaction
        self.consecutive_tool_count = 0
        # Maximum number of consecutive tool calls allowed before forcing ask_human
        self.max_consecutive_tools = 10

    def run(self):
        # Try to load saved conversation context
        conversation = load_conversation()

        # Check if this is a restart initiated by the agent
        agent_initiated_restart = False
        if conversation:
            print("Restored previous conversation context")
            agent_initiated_restart = check_for_agent_restart(conversation)
            # If we're continuing after a restart, add a system message to inform the agent
            if agent_initiated_restart:
                conversation.append({
                    "role": "user",
                    "content": "The program has restarted and is continuing execution automatically. Please continue from where you left off."
                })
                self.read_user_input = False
        else:
            conversation = []

        # Set the global conversation context reference
        set_conversation_context(conversation)

        while True:
            tool_count_object = [self.consecutive_tool_count]
            message = get_new_message(self.is_team_mode, tool_count_object, self.read_user_input)
            self.consecutive_tool_count = tool_count_object[0]
            if message is not None:
                conversation.append(message)

            response = run_inference(conversation, self.client, self.tools, self.consecutive_tool_count,
                                     self.max_consecutive_tools)
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
                        print(
                            f"\033[96mConsecutive tool count: {self.consecutive_tool_count}/{self.max_consecutive_tools}\033[0m")

                    result = execute_tool(self.tools, block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })

            # 2) First, append the assistant's own message (including its tool_use blocks!)
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

            # 3) If there were any tool calls, follow up with tool_results as a user turn
            if tool_results:
                self.read_user_input = False
                deal_with_tool_results(tool_results, conversation)
            else:
                self.read_user_input = not self.is_team_mode
