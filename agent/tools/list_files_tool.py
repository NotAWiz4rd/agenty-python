# list_files_tool.py

from tools.base_tool import ToolDefinition

# ------------------------------------------------------------------
# Input‐schema for the list_files tool
# ------------------------------------------------------------------
ListFilesInputSchema = {
    "type": "object",
    "properties": {
        "path": {
            "type": "string",
            "description": "Optional relative path to list files from. Defaults to current directory if not provided."
        }
    },
    "required": ["path"]
}

excluded_folders = {
    ".git",  # Git metadata
    ".hg",  # Mercurial metadata
    ".svn",  # Subversion metadata
    ".idea",  # PyCharm/IntelliJ configs
    ".vscode",  # VS Code configs
    "__pycache__",  # Python bytecode
    "venv",  # Python virtual environments
    ".venv",  # Python virtual environments
    "env",  # alternative venv name
    ".mypy_cache",  # mypy type-checking cache
    ".pytest_cache",  # pytest cache
    ".tox",  # tox environments
    ".eggs",  # setuptools build dirs
    "dist",  # build output
    "build",  # build output
    "node_modules",  # JavaScript deps
    ".DS_Store",  # macOS system files
    ".coverage",  # coverage.py output
    ".cache",  # general caches
    ".next",  # Next.js builds
    ".parcel-cache",  # Parcel builds
}


def list_files(input_data: dict) -> str:
    """
    Lists all files and directories under `path` (recursively), excluding certain folders.
    Directories end with '/' in the returned list.
    """
    import json
    from pathlib import Path

    # support raw JSON string or already-parsed dict
    if isinstance(input_data, str):
        input_data = json.loads(input_data)

    path_str = input_data.get("path", "") or "."
    base = Path(path_str)

    if not base.exists():
        raise FileNotFoundError(f"Path does not exist: {path_str}")
    if not base.is_dir():
        raise NotADirectoryError(f"Not a directory: {path_str}")

    entries = []
    for entry in base.rglob('*'):
        if any(part in excluded_folders for part in entry.parts):
            continue

        rel = entry.relative_to(base)
        entries.append(str(rel) + ('/' if entry.is_dir() else ''))

    return json.dumps(entries)


# ------------------------------------------------------------------
# ToolDefinition instance
# ------------------------------------------------------------------
ListFilesDefinition = ToolDefinition(
    name="list_files",
    description="List files and directories at a given path. If no path is provided, lists files in the current directory.",
    input_schema=ListFilesInputSchema,
    function=list_files
)
