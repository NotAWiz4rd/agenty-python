"""Unit tests for agent/tools/send_agent_message_tool.py"""
import pytest
import requests

import tools.send_agent_message_tool as samt
from tools.send_agent_message_tool import send_agent_message


@pytest.fixture(autouse=True)
def reset_agent_endpoints():
    """Reset cached AGENT_ENDPOINTS before and after each test."""
    samt.AGENT_ENDPOINTS = None
    yield
    samt.AGENT_ENDPOINTS = None


def _set_endpoints(endpoints: dict):
    samt.AGENT_ENDPOINTS = endpoints


class TestSendAgentMessageTool:
    def test_posts_to_correct_agent_url(self, mocker):
        _set_endpoints({"Bob": "http://bob-host:8082"})
        mock_post = mocker.patch("tools.send_agent_message_tool.requests.post")
        mock_post.return_value = mocker.MagicMock(status_code=200)
        mock_post.return_value.raise_for_status = lambda: None

        send_agent_message({"target_agent": "Bob", "from_agent": "Alice", "message": "hi"})

        mock_post.assert_called_once()
        call_url = mock_post.call_args[0][0]
        assert "bob-host:8082" in call_url
        assert "/send-message" in call_url

    def test_returns_success_on_200(self, mocker):
        _set_endpoints({"Bob": "http://bob-host:8082"})
        mock_post = mocker.patch("tools.send_agent_message_tool.requests.post")
        mock_post.return_value = mocker.MagicMock(status_code=200)
        mock_post.return_value.raise_for_status = lambda: None

        result = send_agent_message({"target_agent": "Bob", "from_agent": "Alice", "message": "hi"})
        assert "Bob" in result
        assert "hi" in result

    def test_returns_error_when_target_agent_unknown(self, mocker):
        _set_endpoints({"Alice": "http://alice:8081"})

        result = send_agent_message({"target_agent": "Unknown", "from_agent": "Alice", "message": "hi"})
        assert "Unknown" in result or "unknown" in result.lower()

    def test_returns_error_on_connection_error(self, mocker):
        _set_endpoints({"Bob": "http://bob-host:8082"})
        mocker.patch(
            "tools.send_agent_message_tool.requests.post",
            side_effect=requests.ConnectionError("timeout"),
        )
        result = send_agent_message({"target_agent": "Bob", "from_agent": "Alice", "message": "hi"})
        assert "offline" in result.lower() or "Failed" in result

    def test_returns_error_on_timeout(self, mocker):
        _set_endpoints({"Bob": "http://bob-host:8082"})
        mocker.patch(
            "tools.send_agent_message_tool.requests.post",
            side_effect=requests.Timeout("timed out"),
        )
        result = send_agent_message({"target_agent": "Bob", "from_agent": "Alice", "message": "hi"})
        assert "Failed" in result or "Error" in result

    def test_loads_endpoints_from_team_config_when_none(self, mocker):
        mock_endpoints = {"Bob": "http://bob:8082"}
        mocker.patch("tools.send_agent_message_tool.get_agent_endpoints", return_value=mock_endpoints)
        mock_post = mocker.patch("tools.send_agent_message_tool.requests.post")
        mock_post.return_value = mocker.MagicMock(status_code=200)
        mock_post.return_value.raise_for_status = lambda: None

        send_agent_message({"target_agent": "Bob", "from_agent": "Alice", "message": "hi"})
        assert samt.AGENT_ENDPOINTS is not None
