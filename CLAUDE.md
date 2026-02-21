# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Agenty is a self-extending AI multi-agent system where agents can write tools for themselves, collaborate via group chat, and maintain conversation context across restarts. The system supports both single-agent and experimental multi-agent (team) modes.

## Project Structure

```
agent/          - Core agent implementation and tools
  base_agent.py    - Main agent loop and message handling
  main.py          - Entry point with Docker/standalone config
  api.py           - FastAPI server for agent communication
  llm.py           - LLM inference with retry logic
  tools/           - Modular tool definitions
  context_handling.py - Context persistence and message queue
  tools_utils.py   - Tool registration and execution

group_chat/     - Shared communication service
  group_chat.py    - Message storage and retrieval API

oversight_officer/ - Optional: monitors suspicious agent activity
group_work_log/    - Optional: aggregates and summarizes team work
```

## Running the System

### Single Agent Mode
```bash
# Set API key
export ANTHROPIC_API_KEY=your_key_here

# Run single agent
python agent/main.py
```

### Team Mode (Docker)
```bash
# Configure team-config.json with task and agents
# Deploy team with default profiles
./scripts/deploy_agent_team.sh

# With optional services
./scripts/deploy_agent_team.sh --with-group-work-log --with-oversight-officer

# Manage team
./scripts/pause_agent_team.sh    # Stop containers
./scripts/resume_agent_team.sh   # Restart containers
./scripts/undeploy_agent_team.sh # Full cleanup
```

### Docker Agent Configuration
When running multiple agents, use Docker arguments:
```bash
python agent/main.py --docker_mode True --docker_agent_index 0 --docker_host_base agent
```

## Architecture Patterns

### Agent Loop (base_agent.py)
The agent runs an infinite loop that:
1. Checks for new messages (group chat, direct messages, user input)
2. Runs LLM inference with available tools
3. Executes tool calls and collects results
4. Tracks consecutive tool usage (max 20 before requiring human check-in in single-agent mode)
5. Auto-restarts when token limit (50k) is reached, preserving context via summary

### Communication Flow
- **Single-agent mode**: Direct user input via stdin
- **Team mode**:
  - Messages queued via FastAPI endpoints (`/send-message`)
  - Agents poll group chat service for broadcasts
  - Direct agent-to-agent messaging via agent API ports

### Context Persistence
- Conversation saved to `conversation_context.pkl` on restart
- Context loaded on startup, appends auto-message to continue
- Context deleted on clean exit, preserved on errors
- System flags: `sys.is_restarting`, `sys.is_error_exit`

### Tool System
Tools are defined in `agent/tools/` following the `ToolDefinition` pattern:
```python
ToolDefinition(
    name="tool_name",
    description="What it does",
    input_schema={"type": "object", "properties": {...}, "required": [...]},
    function=callable
)
```

Tools registered in `tools_utils.get_tool_list()`. Team-mode-only tools: `send_group_message`, `send_agent_message`, `wait`, `report_suspicious_activity`.

### Token Management
- Prompt caching: Last 3 cache control markers kept via `remove_all_but_last_three_cache_controls()`
- Auto-restart at 50k tokens with LLM-generated summary
- Token usage tracked and displayed per inference

### LLM Configuration
- Model: `claude-sonnet-4-20250514` (see llm.py:77)
- Max tokens: 9999
- Retry logic: 5 attempts for 429, 500, 529 errors with 3s delays
- Web search tool: `web_search_20250305` with max 3 uses

### Team Mode Specifics
- Agent names loaded from `team-config.json` via `team_config_loader.py`
- Each agent runs FastAPI server on configured port (see `team-config.json`)
- Group chat stores messages in `chat_messages.txt` with format: `username||timestamp||message`
- Turn delay calculated: `(number_of_agents - 1) * 2000ms` to avoid rate limits

## Development Commands

### Installing Dependencies
```bash
pip install -r requirements.txt
```

### Running Tests
No test suite currently exists in the repository.

### Viewing Logs
```bash
# Agent errors
cat error.txt

# Group chat messages
cat group_chat/chat_messages.txt

# Docker logs
docker compose logs -f agent
docker compose logs -f group_chat
```

### Monitoring
```bash
# Agent health
curl http://localhost:8081/health

# Group chat status
curl http://localhost:5000/status

# Monitor dashboard
curl http://localhost:8080/health

# Frontend dashboard
open http://localhost:3000
```

## Key Implementation Details

### Agent Restart Flow
1. Tool returns `{"restart": true}` or `{"restart": true, "reset_context": true}`
2. `deal_with_tool_results()` detects restart signal
3. If reset_context: restart without saving (tools: `reset_context_tool.py`)
4. Otherwise: save conversation and exec Python with same args (tools: `restart_program_tool.py`)

### Creating New Tools
Agents can create tools dynamically via `create_tool` (see `create_tool_tool.py`):
1. Agent writes new Python module in `agent/tools/`
2. Tool must follow `ToolDefinition` pattern
3. Agent restarts to load new tool
4. Tool registered in `tools_utils.py` imports

### Team Communication
- **Group Chat**: Broadcast to all agents via `/send` endpoint
- **Direct Message**: Target specific agent via agent's `/send-message` endpoint
- **Message Queue**: Each agent has thread-safe queue for incoming messages

### Docker Deployment Details
- Shared git volume `agents_git_remote` for team collaboration
- Agent containers scaled via `--scale agent=N`
- Profiles: `agent` (default), `group_work_log`, `oversight_officer`
- Initial task set in `.env` as `INITIAL_GROUP_CHAT_MESSAGE`

## Important Notes

- Team mode is experimental (see README.md:7-9)
- Set `TEAM_MODE` in base_agent.py is outdated; now determined by agent count in config
- Consecutive tool limit only enforced in single-agent mode
- Context files (`conversation_context.pkl`) should be gitignored
- Agent automatically delays turns in team mode to prevent rate limiting
- Frontend requires Node 18+ and runs on port 3000
