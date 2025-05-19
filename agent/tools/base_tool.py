class ToolDefinition:
    def __init__(self, name: str, description: str, input_schema: dict, function):
        self.name = name
        self.description = description
        self.input_schema = input_schema
        self.function = function
