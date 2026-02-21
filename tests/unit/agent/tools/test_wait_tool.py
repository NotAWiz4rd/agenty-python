"""Unit tests for agent/tools/wait_tool.py"""
import pytest

from tools.wait_tool import wait


class TestWaitTool:
    def test_calls_sleep_with_correct_seconds(self, mocker):
        mock_sleep = mocker.patch("tools.wait_tool.time.sleep")
        wait({"seconds": 5})
        mock_sleep.assert_called_once_with(5)

    def test_calls_sleep_with_float_seconds(self, mocker):
        mock_sleep = mocker.patch("tools.wait_tool.time.sleep")
        wait({"seconds": 2.5})
        mock_sleep.assert_called_once_with(2.5)

    def test_returns_confirmation_message(self, mocker):
        mocker.patch("tools.wait_tool.time.sleep")
        result = wait({"seconds": 3})
        assert "3" in result
        assert "Waited" in result or "waited" in result.lower()

    def test_zero_seconds_is_valid(self, mocker):
        mock_sleep = mocker.patch("tools.wait_tool.time.sleep")
        result = wait({"seconds": 0})
        mock_sleep.assert_called_once_with(0)
        assert isinstance(result, str)

    def test_rejects_negative_duration(self):
        with pytest.raises(ValueError):
            wait({"seconds": -1})

    def test_rejects_negative_float(self):
        with pytest.raises(ValueError):
            wait({"seconds": -0.5})

    def test_rejects_non_numeric_seconds(self):
        with pytest.raises((ValueError, TypeError)):
            wait({"seconds": "fast"})
