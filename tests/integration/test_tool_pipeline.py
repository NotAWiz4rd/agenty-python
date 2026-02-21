"""Integration tests: tool registration → execution pipeline."""
import pytest

from tools_utils import deal_with_tool_results, execute_tool, get_tool_list
from tools.base_tool import ToolDefinition


class TestToolPipeline:
    def test_get_tool_list_functions_are_callable(self):
        tools = get_tool_list(is_team_mode=False)
        for t in tools:
            assert callable(t.function), f"{t.name} function is not callable"

    def test_execute_tool_reads_real_file(self, tmp_working_dir):
        (tmp_working_dir / "test.txt").write_text("integration content")
        tools = get_tool_list(is_team_mode=False)
        result = execute_tool(tools, "read_file", {"path": "test.txt"})
        assert "integration content" in result

    def test_execute_tool_propagates_error_as_string(self, tmp_working_dir):
        tools = get_tool_list(is_team_mode=False)
        result = execute_tool(tools, "read_file", {"path": "nonexistent.txt"})
        assert isinstance(result, str)
        assert "nonexistent" in result.lower() or "not found" in result.lower()

    def test_execute_tool_returns_not_found_for_unknown_tool(self):
        tools = get_tool_list(is_team_mode=False)
        result = execute_tool(tools, "totally_fake_tool", {})
        assert "not found" in result.lower() or isinstance(result, str)

    def test_deal_with_tool_results_no_restart_on_normal_result(self, mocker):
        mock_restart = mocker.patch("tools_utils.save_conv_and_restart")
        mock_execv = mocker.patch("tools_utils.os.execv")

        conversation = []
        tools = get_tool_list(is_team_mode=False)
        file_result = execute_tool(tools, "list_files", {"path": "."})
        tool_results = [{"type": "tool_result", "content": file_result}]
        deal_with_tool_results(tool_results, conversation)

        mock_restart.assert_not_called()
        mock_execv.assert_not_called()

    def test_deal_with_tool_results_triggers_restart(self, mocker):
        mock_restart = mocker.patch("tools_utils.save_conv_and_restart")
        conversation = []
        tool_results = [{"type": "tool_result", "content": '{"restart": true}'}]
        deal_with_tool_results(tool_results, conversation)
        mock_restart.assert_called_once()

    def test_list_files_tool_returns_parsed_results(self, tmp_working_dir):
        import json
        (tmp_working_dir / "a.txt").write_text("x")
        (tmp_working_dir / "b.txt").write_text("y")
        tools = get_tool_list(is_team_mode=False)
        result = execute_tool(tools, "list_files", {"path": "."})
        parsed = json.loads(result)
        assert isinstance(parsed, list)
        assert len(parsed) >= 2
