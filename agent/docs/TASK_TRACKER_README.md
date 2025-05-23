# Task Tracker Tool

A comprehensive task management system for coordinating work between multiple agents in team mode.

## Overview

The Task Tracker tool provides persistent task management capabilities that survive agent restarts and allow teams to coordinate work effectively. Tasks are stored in a JSON file and include status tracking, assignment, and timestamps.

## Features

- **Create Tasks**: Add new tasks with descriptions and optional assignment
- **List Tasks**: View all tasks or filter by status
- **Update Status**: Change task status (pending → in-progress → completed)
- **Task Assignment**: Assign tasks to specific agents
- **Task Details**: Get full information about any task
- **Persistent Storage**: Tasks survive agent restarts

## Usage

### Add a New Task
```json
{
  "action": "add_task",
  "description": "Task description here",
  "assigned_to": "Agent-Name" // optional
}
```

### List Tasks
```json
{
  "action": "list_tasks",
  "status_filter": "pending" // optional: "pending", "in-progress", "completed", "all"
}
```

### Update Task Status
```json
{
  "action": "update_status",
  "task_id": 1,
  "status": "in-progress" // "pending", "in-progress", or "completed"
}
```

### Get Task Details
```json
{
  "action": "get_details",
  "task_id": 1
}
```

### Assign/Reassign Task
```json
{
  "action": "assign_task",
  "task_id": 1,
  "assigned_to": "Agent-Name"
}
```

## Task Statuses

- **pending**: Task created but not started
- **in-progress**: Task actively being worked on
- **completed**: Task finished

## Data Storage

Tasks are stored in `team_tasks.json` with the following structure:
```json
{
  "next_id": 3,
  "tasks": [
    {
      "id": 1,
      "description": "Task description",
      "status": "pending",
      "assigned_to": "Agent-Name",
      "created": "2025-01-23T10:30:00.123456",
      "updated": "2025-01-23T10:30:00.123456"
    }
  ]
}
```

## Team Workflow Examples

### Starting a New Project
1. Create high-level tasks for project phases
2. Assign tasks to available agents
3. Agents update status as they work
4. Use task listing to track overall progress

### Daily Standups
- List all in-progress tasks to see current work
- List pending tasks to plan next priorities
- Check completed tasks for recent accomplishments

### Handoffs
- Agent A creates a task and assigns to Agent B
- Agent B updates status to in-progress when starting
- Agent B marks completed when finished

## Integration

The tool is automatically available to all agents in team mode and integrates seamlessly with the existing agent framework. No additional setup required beyond the initial tool installation.