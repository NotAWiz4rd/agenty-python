"""Unit tests for agent/util.py"""
import pytest

from util import get_agent_turn_delay_in_ms, get_new_messages_from_group_chat, log_error


# ---------------------------------------------------------------------------
# get_agent_turn_delay_in_ms
# ---------------------------------------------------------------------------

class TestGetAgentTurnDelay:
    def test_one_agent_returns_zero(self):
        assert get_agent_turn_delay_in_ms(1) == 0

    def test_two_agents(self):
        assert get_agent_turn_delay_in_ms(2) == 2000

    def test_three_agents(self):
        assert get_agent_turn_delay_in_ms(3) == 4000

    def test_formula_n_minus_one_times_2000(self):
        for n in range(1, 10):
            assert get_agent_turn_delay_in_ms(n) == (n - 1) * 2000

    def test_custom_ms_per_agent(self):
        assert get_agent_turn_delay_in_ms(3, ms_per_additional_agent=1000) == 2000


# ---------------------------------------------------------------------------
# log_error
# ---------------------------------------------------------------------------

class TestLogError:
    def test_writes_message_to_error_file(self, tmp_working_dir):
        log_error("something broke")
        error_file = tmp_working_dir / "error.txt"
        assert error_file.exists()
        content = error_file.read_text()
        assert "something broke" in content

    def test_appends_when_file_exists(self, tmp_working_dir):
        log_error("first error")
        log_error("second error")
        content = (tmp_working_dir / "error.txt").read_text()
        assert "first error" in content
        assert "second error" in content

    def test_includes_timestamp(self, tmp_working_dir):
        log_error("test")
        content = (tmp_working_dir / "error.txt").read_text()
        # Timestamp format: [YYYY-MM-DD HH:MM:SS]
        assert "[" in content and "]" in content

    def test_does_not_raise_on_write_error(self, monkeypatch):
        # Patch open to simulate a write failure; function should not raise
        import builtins
        original_open = builtins.open

        def bad_open(path, *args, **kwargs):
            if "error.txt" in str(path):
                raise PermissionError("no write access")
            return original_open(path, *args, **kwargs)

        monkeypatch.setattr(builtins, "open", bad_open)
        # Should not raise
        log_error("test")


# ---------------------------------------------------------------------------
# get_new_messages_from_group_chat
# ---------------------------------------------------------------------------

class TestGetNewMessagesFromGroupChat:
    def test_returns_new_messages_on_200(self, mocker):
        mock_response = mocker.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"username": "Alice", "message": "hi"},
            {"username": "Bob", "message": "hello"},
        ]
        mocker.patch("util.requests.get", return_value=mock_response)

        result = get_new_messages_from_group_chat([])
        assert len(result) == 2

    def test_filters_already_seen_messages(self, mocker):
        existing = [{"username": "Alice", "message": "hi"}]
        mock_response = mocker.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"username": "Alice", "message": "hi"},
            {"username": "Bob", "message": "hello"},
        ]
        mocker.patch("util.requests.get", return_value=mock_response)

        result = get_new_messages_from_group_chat(existing)
        assert len(result) == 1
        assert result[0]["username"] == "Bob"

    def test_returns_empty_list_on_connection_error(self, mocker):
        import requests
        mocker.patch("util.requests.get", side_effect=requests.ConnectionError())
        result = get_new_messages_from_group_chat([])
        assert result == []

    def test_returns_empty_list_on_non_200_status(self, mocker):
        mock_response = mocker.MagicMock()
        mock_response.status_code = 500
        mocker.patch("util.requests.get", return_value=mock_response)
        result = get_new_messages_from_group_chat([])
        assert result == []

    def test_returns_empty_list_when_no_new_messages(self, mocker):
        msgs = [{"username": "Alice", "message": "hi"}]
        mock_response = mocker.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = msgs
        mocker.patch("util.requests.get", return_value=mock_response)

        result = get_new_messages_from_group_chat(msgs)
        assert result == []
