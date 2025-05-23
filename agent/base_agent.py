#!/usr/bin/env python3
import json
import os
import sys

from agent.context_handling import set_conversation_context, load_conversation
from agent.llm import run_inference
from agent.tools.restart_program_tool import save_conv_and_restart
from agent.tools_utils import get_tool_list, execute_tool
from agent.util import check_for_agent_restart, get_user_message


class Agent:
    def __init__(self, client, team_mode):
        self.client = client
        self.tools = get_tool_list(team_mode)
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
        else:
            conversation = []

        # Set the global conversation context reference
        set_conversation_context(conversation)

        read_user_input = not agent_initiated_restart

        while True:
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
                    break
                conversation.append({"role": "user", "content": user_input})
                # Reset consecutive tool count when user provides input
                self.consecutive_tool_count = 0

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
