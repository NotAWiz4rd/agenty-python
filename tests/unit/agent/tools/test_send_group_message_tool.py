"""Unit tests for agent/tools/send_group_message_tool.py"""
import pytest
import requests

from tools.send_group_message_tool import send_group_message


class TestSendGroupMessageTool:
    def test_posts_to_group_chat_endpoint(self, mocker):
        mock_post = mocker.patch("tools.send_group_message_tool.requests.post")
        mock_post.return_value = mocker.MagicMock(status_code=200)
        mock_post.return_value.raise_for_status = lambda: None

        send_group_message({"from_agent": "Alice", "message": "hello"})

        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert "/send" in args[0]

    def test_posts_correct_payload(self, mocker):
        mock_post = mocker.patch("tools.send_group_message_tool.requests.post")
        mock_post.return_value = mocker.MagicMock(status_code=200)
        mock_post.return_value.raise_for_status = lambda: None

        send_group_message({"from_agent": "Alice", "message": "hi there"})

        _, kwargs = mock_post.call_args
        assert kwargs["json"]["username"] == "Alice"
        assert kwargs["json"]["message"] == "hi there"

    def test_returns_success_message_on_200(self, mocker):
        mock_post = mocker.patch("tools.send_group_message_tool.requests.post")
        mock_post.return_value = mocker.MagicMock(status_code=200)
        mock_post.return_value.raise_for_status = lambda: None

        result = send_group_message({"from_agent": "Bob", "message": "test"})
        assert "Bob" in result
        assert "test" in result

    def test_returns_error_message_on_connection_failure(self, mocker):
        mocker.patch(
            "tools.send_group_message_tool.requests.post",
            side_effect=requests.ConnectionError("refused"),
        )
        result = send_group_message({"from_agent": "Bob", "message": "test"})
        assert "Failed" in result or "Error" in result

    def test_returns_error_on_http_error_status(self, mocker):
        mock_resp = mocker.MagicMock(status_code=500)
        mock_resp.raise_for_status.side_effect = requests.HTTPError("500")
        mocker.patch("tools.send_group_message_tool.requests.post", return_value=mock_resp)

        result = send_group_message({"from_agent": "Bob", "message": "test"})
        assert "Failed" in result or "Error" in result

    def test_returns_error_when_from_agent_missing(self):
        result = send_group_message({"message": "hello"})
        assert "required" in result.lower() or "Error" in result

    def test_returns_error_when_message_missing(self):
        result = send_group_message({"from_agent": "Alice"})
        assert "required" in result.lower() or "Error" in result
