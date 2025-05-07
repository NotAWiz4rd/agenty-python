# delete_file_tool.py

import json
from pathlib import Path

from tools.base_tool import ToolDefinition

# ------------------------------------------------------------------
# Input‐schema for the delete_file tool
# ------------------------------------------------------------------
DeleteFileInputSchema = {
    "type": "object",
    "properties": {
        "path": {
            "type": "string",
            "description": "The relative path of the file to delete."
        }
    },
    "required": ["path"]
}


def delete_file(input_data: dict) -> str:
    """
    Deletes the file at `path`.
    Raises if path is empty, doesn't exist, or is a directory.
    """
    # allow raw JSON string or parsed dict
    if isinstance(input_data, str):
        input_data = json.loads(input_data)

    path_str = input_data.get("path", "")
    if not path_str:
        raise ValueError("path must be provided")

    file_path = Path(path_str)

    if not file_path.exists():
        raise FileNotFoundError(f"file does not exist: {path_str}")
    if file_path.is_dir():
        raise IsADirectoryError(f"cannot delete directories, '{path_str}' is a directory")

    try:
        file_path.unlink()
    except Exception as e:
        raise RuntimeError(f"failed to delete file: {e}")

    return f"Successfully deleted file: {path_str}"


# ------------------------------------------------------------------
# ToolDefinition instance
# ------------------------------------------------------------------
DeleteFileDefinition = ToolDefinition(
    name="delete_file",
    description="Delete a file at the given path. This operation cannot be undone, so use with caution.",
    input_schema=DeleteFileInputSchema,
    function=delete_file
)
