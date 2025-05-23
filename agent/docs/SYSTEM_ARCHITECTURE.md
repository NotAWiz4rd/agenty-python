# Multi-Agent System Architecture Documentation

## Overview

This is a sophisticated multi-agent system built on top of the Anthropic Claude API, designed to enable multiple AI agents to collaborate and coordinate tasks effectively.

## Core Components

### 1. Base Agent (`base_agent.py`)
- Main agent class that handles conversation flow and tool execution
- Manages conversation context and state persistence
- Implements consecutive tool call limits to prevent infinite loops
- Supports both team mode and individual mode operation

### 2. Team Mode Features
- **Team Mode Flag**: Set via `TEAM_MODE = True` in `main.py`
- **Message Queue**: Automated message handling for inter-agent communication
- **Group Chat**: Agents can send messages to team via `send_group_message` tool
- **Shared Task Management**: Persistent task tracking across all agents

### 3. Tool System
The system includes a comprehensive set of tools:

#### File Operations
- `read_file`: Read file contents with optional line range
- `edit_file`: Make precise text replacements in files
- `delete_file`: Remove files (with caution warnings)
- `list_files`: Directory and file listing

#### Development Tools
- `git_command`: Execute git operations
- `calculator`: Mathematical computations and expressions
- `create_tool`: Dynamic tool creation for new capabilities

#### Team Coordination
- `task_tracker`: Full task management (add, assign, update, list)
- `send_group_message`: Inter-agent communication
- `ask_human`: Request human input/clarification

#### System Management
- `restart_program`: Restart with context preservation
- `reset_context`: Clean slate restart
- `wait`: Pause execution for specified duration

### 4. Task Management System

#### Features
- **Persistent Storage**: Tasks survive agent restarts via `team_tasks.json`
- **Status Tracking**: pending → in-progress → completed workflow
- **Assignment System**: Tasks can be assigned to specific agents
- **Filtering**: List tasks by status or show all
- **Timestamps**: Creation and update tracking

#### Task Workflow
1. Any agent can create tasks with descriptions
2. Tasks can be assigned to specific agents
3. Agents update status as they work
4. Full task details available on demand
5. Tasks persist across system restarts

### 5. Context Management
- **Conversation Persistence**: Context saved across restarts
- **Error Recovery**: Context preserved even on crashes
- **Automatic Restoration**: Seamless continuation after restarts
- **Cleanup Handling**: Proper context management on exit

## Architecture Benefits

### For Team Collaboration
- **Shared State**: All agents see the same task list
- **Clear Ownership**: Task assignment prevents duplicate work
- **Progress Tracking**: Real-time status updates
- **Communication**: Group messaging for coordination

### For Development
- **Tool Extensibility**: Easy to add new capabilities
- **Error Resilience**: Context preservation prevents lost work
- **Debugging Support**: Comprehensive logging and error handling
- **Flexibility**: Supports both team and individual operation modes

### For Reliability
- **Consecutive Tool Limits**: Prevents infinite loops
- **Context Preservation**: No work lost on restarts
- **Graceful Error Handling**: System continues despite errors
- **Clean Shutdown**: Proper cleanup procedures

## Usage Patterns

### Team Coordination
1. Agents create high-level project tasks
2. Tasks get assigned to appropriate agents
3. Agents update status as work progresses
4. Team uses group chat for real-time coordination
5. Progress tracked via task listing

### Individual Development
- Full file system access for code development
- Git integration for version control
- Calculator for computational tasks
- Context preservation for long-running work

## Technical Implementation

### Key Design Decisions
- **Tool-based Architecture**: Modular, extensible design
- **JSON Storage**: Simple, readable persistence format
- **Conversation Context**: Natural language state management
- **Error Recovery**: Robust restart and continuation mechanisms

### Security Considerations
- File operations limited to working directory
- No arbitrary code execution (beyond tool system)
- Human confirmation available for critical decisions
- Clean separation of concerns

This architecture enables effective multi-agent collaboration while maintaining individual agent autonomy and system reliability.