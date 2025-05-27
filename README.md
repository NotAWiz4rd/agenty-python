# Agenty - Self-Extending AI Agent System

This is an AI agent system that can self-extend by writing more tools for itself,
interact with files, execute Git commands, maintain conversation context across restarts,
and incorporate human feedback when needed.

## Features

- File operations (read, edit, delete)
- Directory listing
- Git command execution
- Program restart with context preservation
- Context reset capability
- Human interaction and feedback loop
- Safety mechanisms to prevent excessive tool usage
- Self-extension capabilities
- Error logging and handling

## Getting Started

To start the AI agent system:

1. Ensure all dependencies are installed
2. If using a group-work-repository, create a local directory, initialise it with `git init`, run the git command `git config receive.denyCurrentBranch updateInstead` to allow push and run the clone_repo.sh script to clone the repository
2. Provide an Anthropic API key in the `ANTHROPIC_API_KEY` environment variable
3. Run the main program file `base_agent.py`
4. Begin interacting with the agent through the provided interface

## Available Tools

The agent comes with several built-in tools:

- `read_file`: Read contents of a file, with optional line range specification
- `list_files`: List files in a directory
- `edit_file`: Create or modify files by replacing specified text
- `delete_file`: Remove files from the system
- `git_command`: Execute Git operations (add, commit, status, etc.)
- `restart_program`: Restart while preserving conversation context
- `reset_context`: Reset the conversation context and restart the program
- `ask_human`: Request information or confirmation from the human user
- `create_tool`: Create a new tool for the agent to use
- `calculator`: Perform basic arithmetic operations

## Safety Mechanisms

The agent includes several safety features:

- **Consecutive Tool Limit**: After 10 consecutive tool calls without human interaction, the agent is forced to check in with the human user
- **Error Logging**: Unhandled exceptions are logged to an error.txt file
- **Context Preservation on Error**: Conversation context is preserved when errors occur
- **Controlled Context Management**: Context can be explicitly reset when needed

## Self-Extension

The agent can extend its capabilities by:

1. Creating new Python modules with custom functionality
2. Integrating these modules with the main agent system
3. Registering new tools in the agent's function registry
4. Using these tools in future interactions by restarting the program

## Context Preservation and Management

The agent provides sophisticated context handling:

- **Preservation**: Saves the current conversation state to a pickle file during restarts
- **Restoration**: Reloads this state after restart to maintain continuity
- **Agent-Initiated Restarts**: Can restart itself while preserving context for operations requiring new tools
- **Context Reset**: Can explicitly reset conversation context when needed
- **Automatic Cleanup**: Context is automatically deleted on normal program exit

## Example Usage

```
User: Create a file called example.txt with "Hello World" in it
Agent: [Creates the file]

User: Read the contents of example.txt
Agent: The file contains: Hello World

User: Add a second line to the file
Agent: [Modifies the file]

User: I'm not sure what to do next
Agent: [Uses ask_human tool to request guidance]

User: Let's commit our changes to git
Agent: [Executes git command to commit the changes]

User: Restart the program
Agent: [Restarts while preserving context]
```
