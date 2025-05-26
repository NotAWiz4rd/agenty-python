def run_inference(conversation, llm_client, tools, consecutive_tool_count, max_consecutive_tools=10):
    tools_param = []
    for t in tools:
        tools_param.append({
            "name": t.name,
            "description": t.description,
            "input_schema": t.input_schema
        })

    # If we've hit our consecutive tool limit, we'll force Claude to use the ask_human tool
    tool_choice = {"type": "auto"}
    if consecutive_tool_count >= max_consecutive_tools:
        print(f"\033[93mForcing human check-in after {max_consecutive_tools} consecutive tool calls\033[0m")
        # Find the ask_human tool
        ask_human_tool = next((t for t in tools if t.name == "ask_human"), None)
        if ask_human_tool:
            # Force the use of ask_human tool
            tool_choice = {
                "type": "tool",
                "name": "ask_human"
            }
            # We'll reset the counter when ask_human is actually executed

    return llm_client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        messages=conversation,
        tool_choice=tool_choice,
        tools=tools_param
    )
