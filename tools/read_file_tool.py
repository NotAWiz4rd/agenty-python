# read_file_tool.py

import json
from pathlib import Path

from tools.base_tool import ToolDefinition

# ------------------------------------------------------------------
# Input‐schema for the read_file tool
# ------------------------------------------------------------------
ReadFileInputSchema = {
    "type": "object",
    "properties": {
        "path": {
            "type": "string",
            "description": "The relative path of a file in the working directory."
        },
        "start_line": {
            "type": "integer",
            "description": "Optional line number to start reading from (1-indexed)."
        },
        "end_line": {
            "type": "integer",
            "description": "Optional line number to end reading at (1-indexed, inclusive)."
        }
    },
    "required": ["path"]
}


def read_file(input_data: dict) -> str:
    """
    Reads the contents of the file at `path`.
    If start_line and/or end_line are provided, returns only that range of lines.
    Raises if the path doesn't exist or points to a directory.
    """
    # allow raw JSON string or parsed dict
    if isinstance(input_data, str):
        input_data = json.loads(input_data)

    path_str = input_data.get("path", "")
    start_line = input_data.get("start_line")
    end_line = input_data.get("end_line")
    
    file_path = Path(path_str)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {path_str}")
    if not file_path.is_file():
        raise IsADirectoryError(f"Expected a file but got a directory: {path_str}")

    # If no line restrictions, return the whole file
    if start_line is None and end_line is None:
        return file_path.read_text()
    
    # Read specific line range
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    # Convert to 0-indexed for Python
    start_idx = max(0, (start_line or 1) - 1)
    # If end_line not specified, read till the end
    end_idx = min(len(lines), end_line) if end_line is not None else len(lines)
    
    return ''.join(lines[start_idx:end_idx])


# ------------------------------------------------------------------
# ToolDefinition instance
# ------------------------------------------------------------------
ReadFileDefinition = ToolDefinition(
    name="read_file",
    description=(
        "Read the contents of a given relative file path. Use this when you want to see what's inside a file. "
        "Do not use this with directory names. Optionally specify start_line and end_line to read only a portion of the file."
    ),
    input_schema=ReadFileInputSchema,
    function=read_file
)
