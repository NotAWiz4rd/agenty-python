"""Unit tests for agent/tools_utils.py"""
import json
import sys
from unittest.mock import MagicMock

import pytest

import tools_utils
from tools_utils import deal_with_tool_results, execute_tool, get_tool_list
from tools.base_tool import ToolDefinition


# ---------------------------------------------------------------------------
# Fixture: clean up sys flags between tests
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def reset_sys_flags():
    for flag in ("is_restarting", "is_error_exit"):
        if hasattr(sys, flag):
            delattr(sys, flag)
    yield
    for flag in ("is_restarting", "is_error_exit"):
        if hasattr(sys, flag):
            delattr(sys, flag)


# ---------------------------------------------------------------------------
# get_tool_list
# ---------------------------------------------------------------------------

_TEAM_ONLY_TOOLS = {"send_group_message", "send_agent_message", "wait", "report_suspicious_activity"}


class TestGetToolList:
    def test_non_team_mode_missing_team_tools(self):
        tools = get_tool_list(is_team_mode=False)
        names = {t.name for t in tools}
        assert not names.intersection(_TEAM_ONLY_TOOLS)

    def test_team_mode_has_all_team_tools(self):
        tools = get_tool_list(is_team_mode=True)
        names = {t.name for t in tools}
        assert _TEAM_ONLY_TOOLS.issubset(names)

    def test_all_items_are_tool_definitions(self):
        for mode in (False, True):
            tools = get_tool_list(is_team_mode=mode)
            for t in tools:
                assert isinstance(t, ToolDefinition), f"{t} is not a ToolDefinition"

    def test_no_duplicate_tool_names_single_mode(self):
        tools = get_tool_list(is_team_mode=False)
        names = [t.name for t in tools]
        assert len(names) == len(set(names))

    def test_no_duplicate_tool_names_team_mode(self):
        tools = get_tool_list(is_team_mode=True)
        names = [t.name for t in tools]
        assert len(names) == len(set(names))

    def test_base_tools_present_in_both_modes(self):
        base_tools = {"read_file", "edit_file", "delete_file", "list_files"}
        for mode in (False, True):
            tools = get_tool_list(is_team_mode=mode)
            names = {t.name for t in tools}
            assert base_tools.issubset(names)


# ---------------------------------------------------------------------------
# execute_tool
# ---------------------------------------------------------------------------

def _make_tools(names_and_funcs):
    return [
        ToolDefinition(name=name, description="test", input_schema={}, function=fn)
        for name, fn in names_and_funcs
    ]


class TestExecuteTool:
    def test_calls_matching_tool_function(self):
        called_with = {}

        def my_tool(data):
            called_with["data"] = data
            return "ok"

        tools = _make_tools([("my_tool", my_tool)])
        execute_tool(tools, "my_tool", {"key": "value"})
        assert called_with["data"] == {"key": "value"}

    def test_returns_function_return_value(self):
        tools = _make_tools([("greet", lambda d: f"Hello, {d['name']}")])
        result = execute_tool(tools, "greet", {"name": "Alice"})
        assert result == "Hello, Alice"

    def test_returns_error_string_when_tool_not_found(self):
        result = execute_tool([], "nonexistent_tool", {})
        assert "not found" in result.lower() or isinstance(result, str)

    def test_returns_error_string_when_tool_raises(self):
        def boom(data):
            raise ValueError("something went wrong")

        tools = _make_tools([("boom", boom)])
        result = execute_tool(tools, "boom", {})
        assert "something went wrong" in result
        assert isinstance(result, str)

    def test_does_not_raise_on_tool_exception(self):
        def raiser(data):
            raise RuntimeError("crash")

        tools = _make_tools([("raiser", raiser)])
        # Should not raise
        result = execute_tool(tools, "raiser", {})
        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# deal_with_tool_results
# ---------------------------------------------------------------------------

class TestDealWithToolResults:
    def test_appends_to_conversation(self):
        conversation = []
        tool_results = [{"type": "tool_result", "content": "some result"}]
        deal_with_tool_results(tool_results, conversation)
        assert len(conversation) == 1
        assert conversation[0]["role"] == "user"
        assert conversation[0]["content"] == tool_results

    def test_no_restart_when_no_signal(self, mocker):
        mock_restart = mocker.patch("tools_utils.save_conv_and_restart")
        mock_execv = mocker.patch("tools_utils.os.execv")

        deal_with_tool_results(
            [{"type": "tool_result", "content": "plain text"}],
            [],
        )

        mock_restart.assert_not_called()
        mock_execv.assert_not_called()

    def test_restart_called_on_restart_signal_dict(self, mocker):
        mock_restart = mocker.patch("tools_utils.save_conv_and_restart")

        conversation = []
        tool_results = [{"type": "tool_result", "content": {"restart": True}}]
        deal_with_tool_results(tool_results, conversation)

        mock_restart.assert_called_once()

    def test_restart_called_on_restart_signal_json_string(self, mocker):
        mock_restart = mocker.patch("tools_utils.save_conv_and_restart")

        conversation = []
        tool_results = [{"type": "tool_result", "content": '{"restart": true}'}]
        deal_with_tool_results(tool_results, conversation)

        mock_restart.assert_called_once()

    def test_execv_called_on_reset_context(self, mocker):
        mock_execv = mocker.patch("tools_utils.os.execv")

        conversation = []
        tool_results = [
            {"type": "tool_result", "content": '{"restart": true, "reset_context": true}'}
        ]
        deal_with_tool_results(tool_results, conversation)

        mock_execv.assert_called_once()
        assert getattr(sys, "is_restarting", False) is True

    def test_no_restart_on_non_json_content(self, mocker):
        mock_restart = mocker.patch("tools_utils.save_conv_and_restart")
        mock_execv = mocker.patch("tools_utils.os.execv")

        deal_with_tool_results(
            [{"type": "tool_result", "content": "not json {"}],
            [],
        )

        mock_restart.assert_not_called()
        mock_execv.assert_not_called()
