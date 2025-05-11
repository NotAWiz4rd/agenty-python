# Agenty - Self-Extending AI Agent System

This is an AI agent system that can self-extend by writing more tools for itself,
interact with files, execute Git commands, and maintain conversation context across restarts.

## Features

- File operations (read, edit, delete)
- Directory listing
- Git command execution
- Program restart with context preservation
- Self-extension capabilities

## Getting Started

To start the AI agent system:

1. Ensure all dependencies are installed
2. Provide an Anthropic API key in the `ANTHROPIC_API_KEY` environment variable
3. Run the main program file `base_agent.py`
4. Begin interacting with the agent through the provided interface

## Available Tools

The agent comes with several built-in tools:

- `read_file`: Read contents of a file
- `list_files`: List files in a directory
- `edit_file`: Create or modify files
- `delete_file`: Remove files
- `git_command`: Execute Git operations
- `restart_program`: Restart while preserving conversation context

## Self-Extension

The agent can extend its capabilities by:

1. Creating new Python modules with custom functionality
2. Integrating these modules with the main agent system
3. Registering new tools in the agent's function registry
4. Using these tools in future interactions by restarting the program

## Context Preservation

When restarting, the agent preserves conversation context by:

- Saving the current conversation state to a pickle file
- Reloading this state after restart
- Maintaining continuity of the interaction

## Example Usage

```
User: Create a file called example.txt with "Hello World" in it
Agent: [Creates the file]

User: Read the contents of example.txt
Agent: The file contains: Hello World

User: Restart the program
Agent: [Restarts while preserving context]
```
