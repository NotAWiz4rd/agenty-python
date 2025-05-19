# git_command_tool.py

import json
import subprocess
import shlex
from agent.tools.base_tool import ToolDefinition

# ------------------------------------------------------------------
# Input‐schema for the git_command tool
# ------------------------------------------------------------------
GitCommandInputSchema = {
    "type": "object",
    "properties": {
        "command": {
            "type": "string",
            "description": "The git command to execute (e.g., 'add', 'commit', 'status', 'push', etc.)"
        },
        "args": {
            "type": "string",
            "description": "Additional arguments for the git command (e.g., file paths for add, message for commit)"
        }
    },
    "required": ["command"]
}


def git_command(input_data: dict) -> str:
    """
    Execute a git command and return the result.
    Returns a JSON string with stdout, stderr, and success status.
    """
    # support raw JSON string or already-parsed dict
    if isinstance(input_data, str):
        input_data = json.loads(input_data)

    command = input_data.get("command", "")
    args = input_data.get("args", "")

    if not command:
        raise ValueError("Git command cannot be empty")

    git_cmd = ["git", command]
    
    if args:
        git_cmd.extend(shlex.split(args))
    
    try:
        # Execute the git command
        process = subprocess.Popen(
            git_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()
        
        result = {
            "success": process.returncode == 0,
            "stdout": stdout.strip(),
            "stderr": stderr.strip(),
            "returncode": process.returncode
        }
        
        return json.dumps(result)
    except Exception as e:
        result = {
            "success": False,
            "error": str(e)
        }
        return json.dumps(result)


# ------------------------------------------------------------------
# ToolDefinition instance
# ------------------------------------------------------------------
GitCommandDefinition = ToolDefinition(
    name="git_command",
    description="Execute git commands like add, commit, status, etc.",
    input_schema=GitCommandInputSchema,
    function=git_command
)