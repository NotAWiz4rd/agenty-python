"""Unit tests for agent/tools/task_tracker_tool.py"""
import json

import pytest

from tools.task_tracker_tool import task_tracker


class TestTaskTrackerTool:
    def test_creates_tracker_file_on_first_use(self, tmp_working_dir):
        task_tracker({"action": "add_task", "description": "First task"})
        assert (tmp_working_dir / "team_tasks.json").exists()

    def test_file_format_is_valid_json(self, tmp_working_dir):
        task_tracker({"action": "add_task", "description": "Task A"})
        content = (tmp_working_dir / "team_tasks.json").read_text()
        data = json.loads(content)
        assert "tasks" in data
        assert "next_id" in data

    def test_add_task_and_list_it_back(self, tmp_working_dir):
        task_tracker({"action": "add_task", "description": "Test task"})
        result = task_tracker({"action": "list_tasks"})
        assert "Test task" in result

    def test_add_task_returns_task_id_in_message(self, tmp_working_dir):
        result = task_tracker({"action": "add_task", "description": "My task"})
        assert "#1" in result
        assert "My task" in result

    def test_mark_task_as_complete(self, tmp_working_dir):
        task_tracker({"action": "add_task", "description": "Task to complete"})
        result = task_tracker({"action": "update_status", "task_id": 1, "status": "completed"})
        assert "completed" in result

    def test_list_tasks_returns_all(self, tmp_working_dir):
        task_tracker({"action": "add_task", "description": "Task 1"})
        task_tracker({"action": "add_task", "description": "Task 2"})
        result = task_tracker({"action": "list_tasks"})
        assert "Task 1" in result
        assert "Task 2" in result

    def test_list_tasks_empty_when_no_tasks(self, tmp_working_dir):
        result = task_tracker({"action": "list_tasks"})
        assert "No tasks" in result

    def test_task_id_increments(self, tmp_working_dir):
        task_tracker({"action": "add_task", "description": "First"})
        result = task_tracker({"action": "add_task", "description": "Second"})
        assert "#2" in result

    def test_get_task_details(self, tmp_working_dir):
        task_tracker({"action": "add_task", "description": "Detailed task"})
        result = task_tracker({"action": "get_details", "task_id": 1})
        assert "Detailed task" in result
        assert "pending" in result

    def test_assign_task(self, tmp_working_dir):
        task_tracker({"action": "add_task", "description": "Assignable task"})
        result = task_tracker({"action": "assign_task", "task_id": 1, "assigned_to": "Alice"})
        assert "Alice" in result

    def test_raises_when_action_missing(self, tmp_working_dir):
        with pytest.raises(ValueError):
            task_tracker({})

    def test_raises_when_description_missing_for_add(self, tmp_working_dir):
        with pytest.raises(ValueError):
            task_tracker({"action": "add_task"})

    def test_update_nonexistent_task_raises(self, tmp_working_dir):
        with pytest.raises(ValueError):
            task_tracker({"action": "update_status", "task_id": 999, "status": "completed"})
