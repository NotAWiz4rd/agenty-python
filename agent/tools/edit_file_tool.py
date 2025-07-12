# edit_file_tool.py

from pathlib import Path

from tools.base_tool import ToolDefinition

# ------------------------------------------------------------------
# Input‐schema for the edit_file tool
# ------------------------------------------------------------------
EditFileInputSchema = {
    "type": "object",
    "properties": {
        "path": {
            "type": "string",
            "description": "The path to the file. If the file does not exist, it will be created if old_str is empty."
        },
        "old_str": {
            "type": "string",
            "description": "Text to search for – must match exactly and occur only once. Must be empty if the file is to be created."
        },
        "new_str": {
            "type": "string",
            "description": "Text to replace old_str with. Must be different from old_str. Must never be empty."
        }
    },
    "required": ["path", "old_str", "new_str"],
}


def edit_file(input_data: dict) -> str:
    """
    Replaces old_str with new_str in the file at `path`.
    If file doesn’t exist and old_str is empty, creates it.
    """
    path = input_data.get("path", "")
    old_str = input_data.get("old_str", "")
    new_str = input_data.get("new_str", "")

    # validation
    if not path or old_str == new_str:
        raise ValueError("invalid input parameters")

    if not new_str:
        raise ValueError("new_str must not be empty")

    file_path = Path(path)

    # create file if missing and old_str is empty
    if not file_path.exists():
        if old_str == "":
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(new_str)
            return f"Successfully created file: {path}"
        else:
            raise FileNotFoundError(f"{path} does not exist")

    # read, replace, write
    content = file_path.read_text()
    updated = content.replace(old_str, new_str)

    if old_str and updated == content:
        raise ValueError("old_str not found in file")

    file_path.write_text(updated)
    return "OK"


# ------------------------------------------------------------------
# ToolDefinition instance
# ------------------------------------------------------------------
EditFileDefinition = ToolDefinition(
    name="edit_file",
    description=(
        "Make edits to a text file.\n\n"
        "Replaces 'old_str' with 'new_str' in the given file. "
        "'old_str' and 'new_str' MUST be different from each other.\n\n"
        "If the file specified with path doesn't exist, it will be created."
    ),
    input_schema=EditFileInputSchema,
    function=edit_file
)
