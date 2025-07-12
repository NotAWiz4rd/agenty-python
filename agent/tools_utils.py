import json
import os
import sys

from tools import (
    SendGroupMessageDefinition,
    SendAgentMessageDefinition,
    CommandLineToolDefinition,
    CreateToolDefinition,
    AskHumanDefinition,
    DeleteFileDefinition,
    EditFileDefinition,
    GitCommandDefinition,
    GracefulShutdownDefinition,
    ListFilesDefinition,
    ReadFileDefinition,
    ReportSuspiciousActivityDefinition,
    ResetContextDefinition,
    RestartProgramDefinition,
    TaskTrackerDefinition,
    WaitDefinition,
)
from util import save_conv_and_restart


def get_tool_list(is_team_mode: bool) -> list:
    """Return the list of tools to be used by the agent."""
    tool_list = [
        ReadFileDefinition,
        ListFilesDefinition,
        EditFileDefinition,
        DeleteFileDefinition,
        GitCommandDefinition,
        CommandLineToolDefinition,
        RestartProgramDefinition,
        ResetContextDefinition,
        #AskHumanDefinition,
        CreateToolDefinition,
        GracefulShutdownDefinition,
        TaskTrackerDefinition,
    ]
    # Only add certain tools if in team mode
    if is_team_mode:
        tool_list.append(SendGroupMessageDefinition)
        tool_list.append(SendAgentMessageDefinition)
        tool_list.append(WaitDefinition)
        tool_list.append(ReportSuspiciousActivityDefinition)

    return tool_list


def execute_tool(tools, tool_name: str, input_data):
    tool_def = next((t for t in tools if t.name == tool_name), None)
    if not tool_def:
        return "tool not found"
    print(f"\033[92mtool\033[0m: {tool_name}({json.dumps(input_data)})")
    try:
        return tool_def.function(input_data)
    except Exception as e:
        return str(e)


def deal_with_tool_results(tool_results, conversation):
    conversation.append({
        "role": "user",
        "content": tool_results
    })

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
