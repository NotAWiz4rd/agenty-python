# task_tracker_tool.py

import json
import os
from datetime import datetime
from pathlib import Path

from tools.base_tool import ToolDefinition

# ------------------------------------------------------------------
# Input schema for the task_tracker tool
# ------------------------------------------------------------------
TaskTrackerInputSchema = {
    "type": "object",
    "properties": {
        "action": {
            "type": "string",
            "description": "Action to perform: add_task, list_tasks, update_status, get_details or assign_task.",
            "enum": ["add_task", "list_tasks", "update_status", "get_details", "assign_task"]
        },
        "description": {
            "type": "string",
            "description": "Task description (required for add_task)."
        },
        "assigned_to": {
            "type": "string",
            "description": "Agent name to assign task to (optional for add_task, required for assign_task)."
        },
        "task_id": {
            "type": "integer",
            "description": "Task ID (required for update_status, get_details, assign_task)."
        },
        "status": {
            "type": "string",
            "description": "New status (required for update_status).",
            "enum": ["pending", "in-progress", "completed"]
        },
        "status_filter": {
            "type": "string",
            "description": "Filter tasks by status (optional for list_tasks).",
            "enum": ["pending", "in-progress", "completed", "all"]
        }
    },
    "required": ["action"]
}

TASKS_FILE = "team_tasks.json"

def load_tasks():
    """Load tasks from JSON file or create empty structure."""
    if os.path.exists(TASKS_FILE):
        try:
            with open(TASKS_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            pass
    return {"next_id": 1, "tasks": []}

def save_tasks(data):
    """Save tasks to JSON file."""
    with open(TASKS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def task_tracker(input_data: dict) -> str:
    """
    Manage tasks for the team with various operations.
    """
    # allow raw JSON string or parsed dict
    if isinstance(input_data, str):
        input_data = json.loads(input_data)

    action = input_data.get("action")
    if not action:
        raise ValueError("action must be provided")

    data = load_tasks()
    
    if action == "add_task":
        description = input_data.get("description")
        if not description:
            raise ValueError("description is required for add_task")
        
        task = {
            "id": data["next_id"],
            "description": description,
            "status": "pending",
            "assigned_to": input_data.get("assigned_to", "unassigned"),
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat()
        }
        
        data["tasks"].append(task)
        data["next_id"] += 1
        save_tasks(data)
        
        return f"Task #{task['id']} created: {description} (assigned to: {task['assigned_to']})"
    
    elif action == "list_tasks":
        status_filter = input_data.get("status_filter", "all")
        tasks = data["tasks"]
        
        if status_filter != "all":
            tasks = [t for t in tasks if t["status"] == status_filter]
        
        if not tasks:
            return f"No tasks found" + (f" with status '{status_filter}'" if status_filter != "all" else "")
        
        result = f"Tasks ({len(tasks)} found):\n"
        for task in tasks:
            result += f"#{task['id']}: {task['description']} [{task['status']}] (assigned to: {task['assigned_to']})\n"
        
        return result.strip()
    
    elif action == "update_status":
        task_id = input_data.get("task_id")
        new_status = input_data.get("status")
        
        if task_id is None:
            raise ValueError("task_id is required for update_status")
        if not new_status:
            raise ValueError("status is required for update_status")
        
        task = next((t for t in data["tasks"] if t["id"] == task_id), None)
        if not task:
            raise ValueError(f"Task #{task_id} not found")
        
        old_status = task["status"]
        task["status"] = new_status
        task["updated"] = datetime.now().isoformat()
        save_tasks(data)
        
        return f"Task #{task_id} status updated from '{old_status}' to '{new_status}'"
    
    elif action == "get_details":
        task_id = input_data.get("task_id")
        if task_id is None:
            raise ValueError("task_id is required for get_details")
        
        task = next((t for t in data["tasks"] if t["id"] == task_id), None)
        if not task:
            raise ValueError(f"Task #{task_id} not found")
        
        return f"""Task #{task['id']} Details:
Description: {task['description']}
Status: {task['status']}
Assigned to: {task['assigned_to']}
Created: {task['created']}
Last updated: {task['updated']}"""
    
    elif action == "assign_task":
        task_id = input_data.get("task_id")
        assigned_to = input_data.get("assigned_to")
        
        if task_id is None:
            raise ValueError("task_id is required for assign_task")
        if not assigned_to:
            raise ValueError("assigned_to is required for assign_task")
        
        task = next((t for t in data["tasks"] if t["id"] == task_id), None)
        if not task:
            raise ValueError(f"Task #{task_id} not found")
        
        old_assignee = task["assigned_to"]
        task["assigned_to"] = assigned_to
        task["updated"] = datetime.now().isoformat()
        save_tasks(data)
        
        return f"Task #{task_id} reassigned from '{old_assignee}' to '{assigned_to}'"
    
    else:
        raise ValueError(f"Unknown action: {action}")


# ------------------------------------------------------------------
# ToolDefinition instance
# ------------------------------------------------------------------
TaskTrackerDefinition = ToolDefinition(
    name="task_tracker",
    description="Manage team tasks with operations to add, list, update status, get details, and assign tasks. Maintains persistent task data across sessions.",
    input_schema=TaskTrackerInputSchema,
    function=task_tracker
)