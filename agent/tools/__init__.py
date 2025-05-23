from .ask_human_tool import AskHumanDefinition
from .calculator_tool import CalculatorDefinition
from .create_tool_tool import CreateToolDefinition
from .delete_file_tool import DeleteFileDefinition
from .edit_file_tool import EditFileDefinition
from .git_command_tool import GitCommandDefinition
from .list_files_tool import ListFilesDefinition
from .read_file_tool import ReadFileDefinition
from .reset_context_tool import ResetContextDefinition
from .restart_program_tool import RestartProgramDefinition
from .send_group_message_tool import SendGroupMessageDefinition
from .send_agent_message_tool import SendAgentMessageDefinition

# Register all tools
TOOLS = [
    ReadFileDefinition,
    ListFilesDefinition,
    EditFileDefinition,
    DeleteFileDefinition,
    GitCommandDefinition,
    AskHumanDefinition,
    SendGroupMessageDefinition,
    SendAgentMessageDefinition,
    CalculatorDefinition,
    ResetContextDefinition,
    RestartProgramDefinition,
    CreateToolDefinition,
]
