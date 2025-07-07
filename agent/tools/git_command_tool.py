# git_command_tool.py

import json
import subprocess
import shlex
import os
from tools.base_tool import ToolDefinition

# ------------------------------------------------------------------
# Input‐schema for the git_command tool
# ------------------------------------------------------------------
GitCommandInputSchema = {
    "type": "object",
    "properties": {
        "command": {
            "type": "string",
            "description": "The git command to execute (e.g., 'add', 'commit', 'status', 'push', 'pull' etc.)."
        },
        "args": {
            "type": "string",
            "description": "Additional arguments for the git command (e.g., file paths for add, message for commit)."
        },
        "use_work_repo": {
            "type": "boolean",
            "description": "When set to TRUE we should use the work_repo directory, if FALSE we use current directory. Default is TRUE."
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
    use_work_repo = input_data.get("use_work_repo", True)

    if not command:
        raise ValueError("Git command cannot be empty")

    # Determine the working directory
    cwd = None
    if use_work_repo:
        current_dir = os.getcwd()
        target_dir = os.path.join(current_dir, "work_repo")
        
        # Check if the specified directory exists
        if not os.path.exists(target_dir):
            result = {
                "success": False,
                "error": f"Working directory does not exist: {target_dir}"
            }
            return json.dumps(result)
        
        cwd = target_dir

    git_cmd = ["git", command]
    
    if args:
        git_cmd.extend(shlex.split(args))
    
    try:
        # Execute the git command
        process = subprocess.Popen(
            git_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=cwd  # This sets the working directory for the command
        )
        stdout, stderr = process.communicate()
        
        result = {
            "success": process.returncode == 0,
            "stdout": stdout.strip(),
            "stderr": stderr.strip(),
            "returncode": process.returncode,
            "use_work_repo": cwd if cwd else os.getcwd()
        }
        
        return json.dumps(result)
    except Exception as e:
        result = {
            "success": False,
            "error": str(e),
            "use_work_repo": cwd if cwd else os.getcwd()
        }
        return json.dumps(result)


# ------------------------------------------------------------------
# ToolDefinition instance
# ------------------------------------------------------------------
GitCommandDefinition = ToolDefinition(
    name="git_command",
    description="Executes git commands such as add, commit, status, push, pull, etc. The optional parameter 'use_work_repo' (default: true) determines whether the command runs in the predefined 'work_repo' directory or in the current directory. The output includes stdout, stderr, and success status.",
    input_schema=GitCommandInputSchema,
    function=git_command
)