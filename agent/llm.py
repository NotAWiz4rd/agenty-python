import json

from agent.team_config_loader import get_current_agent_name

agent_name = get_current_agent_name()
system_prompt = f"You are {agent_name}, an AI assistant working as part of a team of agents. Always identify yourself as {agent_name} when communicating with other agents or humans. Your responses should be helpful, harmless, and honest."


def remove_all_but_last_three_cache_controls(conversation):
    number_of_cache_controls = 3
    cache_control = """, \"cache_control\": {\"type\": \"ephemeral\"}"""
    parts = json.dumps(conversation).split(cache_control)
    count = len(parts) - 1  # number of occurrences

    if count <= number_of_cache_controls:
        return conversation  # Nothing to remove

    # Join: keep the target only for the last n occurrences
    # The first (count - n) splits won't get the target re-inserted
    first_part = ''.join(parts[:count - number_of_cache_controls + 1])
    last_part = cache_control.join(parts[count - number_of_cache_controls + 1:])
    return json.loads(first_part + last_part)


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

    conversation = remove_all_but_last_three_cache_controls(conversation)

    # Filter out any existing 'system' role messages to prevent API errors
    filtered_conversation = [msg for msg in conversation if msg.get("role") != "system"]

    return llm_client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        system=system_prompt,  # Pass system prompt as a top-level parameter
        messages=filtered_conversation,
        tool_choice=tool_choice,
        tools=tools_param
    )
