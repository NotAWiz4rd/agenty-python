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
        }
    },
    "required": ["path"]
}


def read_file(input_data: dict) -> str:
    """
    Reads the contents of the file at `path`.
    Raises if the path doesn't exist or points to a directory.
    """
    # allow raw JSON string or parsed dict
    if isinstance(input_data, str):
        input_data = json.loads(input_data)

    path_str = input_data.get("path", "")
    file_path = Path(path_str)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {path_str}")
    if not file_path.is_file():
        raise IsADirectoryError(f"Expected a file but got a directory: {path_str}")

    return file_path.read_text()


# ------------------------------------------------------------------
# ToolDefinition instance
# ------------------------------------------------------------------
ReadFileDefinition = ToolDefinition(
    name="read_file",
    description=(
        "Read the contents of a given relative file path. Use this when you want to see what's inside a file. "
        "Do not use this with directory names."
    ),
    input_schema=ReadFileInputSchema,
    function=read_file
)
