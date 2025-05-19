from .read_file_tool import ReadFileDefinition
from .list_files_tool import ListFilesDefinition
from .edit_file_tool import EditFileDefinition
from .delete_file_tool import DeleteFileDefinition
from .git_command_tool import GitCommandDefinition

# Register all tools
TOOLS = [
    ReadFileDefinition,
    ListFilesDefinition,
    EditFileDefinition,
    DeleteFileDefinition,
    GitCommandDefinition
]