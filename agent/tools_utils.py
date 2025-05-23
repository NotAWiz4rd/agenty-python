import json

from agent.tools import (
    SendGroupMessageDefinition,
    CreateToolDefinition,
    AskHumanDefinition,
    CalculatorDefinition,
    DeleteFileDefinition,
    EditFileDefinition,
    GitCommandDefinition,
    ListFilesDefinition,
    ReadFileDefinition,
    ResetContextDefinition,
    RestartProgramDefinition
)


def get_tool_list(is_team_mode: bool) -> list:
    """Return the list of tools to be used by the agent."""
    tool_list = [
        ReadFileDefinition,
        ListFilesDefinition,
        EditFileDefinition,
        DeleteFileDefinition,
        GitCommandDefinition,
        RestartProgramDefinition,
        ResetContextDefinition,
        AskHumanDefinition,
        CalculatorDefinition,
        CreateToolDefinition,
    ]
    # Only add certain tools if in team mode
    if is_team_mode:
        tool_list.append(SendGroupMessageDefinition)

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
