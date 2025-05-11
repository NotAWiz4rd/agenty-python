#!/usr/bin/env python3
import json
import os
import pickle
import sys

import anthropic

from tools.delete_file_tool import DeleteFileDefinition
from tools.edit_file_tool import EditFileDefinition
from tools.git_command_tool import GitCommandDefinition
from tools.list_files_tool import ListFilesDefinition
from tools.read_file_tool import ReadFileDefinition
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

    def run(self):
        # Try to load saved conversation context
        conversation = self.load_conversation()
        if conversation:
            print("Restored previous conversation context")
        else:
            conversation = []

        # Set the global conversation context reference
        set_conversation_context(conversation)

        print("Chat with Claude (use 'ctrl+c' to exit)")
        read_user_input = True

        while True:
            if read_user_input:
                # prompt for user
                try:
                    print(f"\033[94mYou\033[0m: ", end="", flush=True)
                    user_input, ok = self.get_user_message()
                except KeyboardInterrupt:
                    sys.exit(0)
                if not ok:
                    break
                conversation.append({"role": "user", "content": user_input})

            response = self.run_inference(conversation)
            tool_results = []

            # print assistant text and collect any tool calls
            for block in response.content:
                if block.type == "text":
                    print(f"\033[93mClaude\033[0m: {block.text}")
                elif block.type == "tool_use":
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

                    # if tool asked for restart, save+restart
                    if payload is not None and payload.get("restart"):
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

        return self.client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=1024,
            messages=conversation,
            tool_choice={"type": "auto"},
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
    try:
        text = input()
        return text, True
    except EOFError:
        return "", False


def main():
    client = anthropic.Anthropic()  # expects ANTHROPIC_API_KEY in env
    tools = [
        ReadFileDefinition,
        ListFilesDefinition,
        EditFileDefinition,
        DeleteFileDefinition,
        GitCommandDefinition,
        RestartProgramDefinition
    ]
    agent = Agent(client, get_user_message, tools)
    agent.run()


if __name__ == "__main__":
    main()
