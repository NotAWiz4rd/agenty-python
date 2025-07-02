# create_tool_tool.py

from tools.base_tool import ToolDefinition

# We are using the schema to force the LLM to think about what it is doing
CreateToolInputSchema = {
    "type": "object",
    "properties": {
        "toolname": {
            "type": "string",
            "description": "The name of the tool to create."
        },
        "description": {
            "type": "string",
            "description": "The description and functions of the tool to create."
        },
    },
    "required": ["toolname", "description"]
}


def create_tool(input_data: dict) -> str:
    return (
        "You can create a tool by looking at the files base_tool.py and delete_file_tool.py. "
        "Then write your tool using the same format by utilising the edit_file tool. You can also use the ask_human "
        "tool to ask for help if you are unsure about specifics. After you've create the new tool file"
        "add it to the tools list in the __init__.py file. Then import it in the base_agent.py file and add it "
        "to the tool list there. Then you should restart yourself so the tool gets loaded.")


# ------------------------------------------------------------------
# ToolDefinition instance
# ------------------------------------------------------------------
CreateToolDefinition = ToolDefinition(
    name="create_tool",
    description=(
        "Create a new tool for yourself, to enable capabilities that you currently lack. "
        "You should always consider using this tool instead of writing a random python script."
        "If in doubt, ask your human whether it makes sense to create a new tool."
    ),
    input_schema=CreateToolInputSchema,
    function=create_tool
)
