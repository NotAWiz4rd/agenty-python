"""Unit tests for agent/llm.py"""
import json
import sys
from unittest.mock import MagicMock, patch

import anthropic
import pytest

from llm import get_system_prompt, remove_all_but_last_three_cache_controls, run_inference


# ---------------------------------------------------------------------------
# Helper: minimal APIStatusError subclass that bypasses httpx requirements
# ---------------------------------------------------------------------------

class FakeAPIStatusError(anthropic.APIStatusError):
    """Minimal subclass to test retry logic without real HTTP objects."""

    def __new__(cls, status_code):
        return Exception.__new__(cls)

    def __init__(self, status_code: int):
        self.status_code = status_code
        self.message = f"Mock API error {status_code}"


def _make_mock_response(text: str = "response", input_tokens: int = 100, output_tokens: int = 50):
    resp = MagicMock()
    resp.content = [MagicMock(text=text)]
    resp.usage.input_tokens = input_tokens
    resp.usage.output_tokens = output_tokens
    return resp


# ---------------------------------------------------------------------------
# get_system_prompt
# ---------------------------------------------------------------------------

class TestGetSystemPrompt:
    def test_single_mode_returns_non_empty(self):
        result = get_system_prompt("Claude")
        assert result and len(result) > 0

    def test_single_mode_contains_agent_name(self):
        result = get_system_prompt("Ziggy")
        assert "Ziggy" in result

    def test_team_mode_contains_agent_name(self):
        result = get_system_prompt("Carmen", is_team_mode=True)
        assert "Carmen" in result

    def test_single_mode_has_no_team_keywords(self):
        result = get_system_prompt("Claude", is_team_mode=False)
        # Single mode should not mention working with a team
        assert "in concert with your team" not in result

    def test_team_mode_has_team_instructions(self):
        result = get_system_prompt("Claude", is_team_mode=True)
        assert "team" in result.lower()

    def test_single_mode_mentions_independence(self):
        result = get_system_prompt("Claude", is_team_mode=False)
        assert "independently" in result


# ---------------------------------------------------------------------------
# remove_all_but_last_three_cache_controls
# ---------------------------------------------------------------------------

def _cc_item(text: str = "hello"):
    """Dict with cache_control (must be last key for predictable JSON ordering)."""
    return {"type": "text", "text": text, "cache_control": {"type": "ephemeral"}}


def _plain_item(text: str = "hello"):
    return {"type": "text", "text": text}


class TestRemoveCacheControls:
    def test_zero_cache_controls_unchanged(self):
        conv = [_plain_item("a"), _plain_item("b")]
        result = remove_all_but_last_three_cache_controls(conv)
        assert result == conv

    def test_exactly_three_unchanged(self):
        conv = [_cc_item("a"), _cc_item("b"), _cc_item("c")]
        result = remove_all_but_last_three_cache_controls(conv)
        assert json.dumps(result).count('"cache_control"') == 3

    def test_five_reduces_cache_controls(self):
        # With 5 cache controls, the function strips the earlier ones.
        # The implementation joins first_part + last_part (no CC at boundary),
        # so count=5 with n=3 results in n-1=2 CCs retained.
        conv = [_cc_item(str(i)) for i in range(5)]
        result = remove_all_but_last_three_cache_controls(conv)
        remaining = json.dumps(result).count('"cache_control"')
        assert remaining < 5  # some were stripped
        assert remaining >= 1  # at least some retained

    def test_four_reduces_cache_controls(self):
        conv = [_cc_item(str(i)) for i in range(4)]
        result = remove_all_but_last_three_cache_controls(conv)
        remaining = json.dumps(result).count('"cache_control"')
        assert remaining < 4  # some were stripped
        assert remaining >= 1  # at least some retained

    def test_does_not_mutate_original(self):
        conv = [_cc_item(str(i)) for i in range(5)]
        original_json = json.dumps(conv)
        remove_all_but_last_three_cache_controls(conv)
        assert json.dumps(conv) == original_json

    def test_result_is_valid_list(self):
        conv = [_cc_item(str(i)) for i in range(5)]
        result = remove_all_but_last_three_cache_controls(conv)
        assert isinstance(result, list)
        assert len(result) == 5


# ---------------------------------------------------------------------------
# run_inference
# ---------------------------------------------------------------------------

class TestRunInference:
    @patch("time.sleep")
    @patch("agent.tools_utils.get_tools_param")
    def test_success_returns_content_and_tokens(self, mock_get_tools, mock_sleep):
        mock_get_tools.return_value = []
        mock_response = _make_mock_response(input_tokens=100, output_tokens=50)
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_response

        content, tokens = run_inference(
            conversation=[{"role": "user", "content": "Hello"}],
            llm_client=mock_client,
            tools=[],
        )

        assert content == mock_response.content
        assert tokens == 150  # 100 + 50

    @patch("time.sleep")
    @patch("agent.tools_utils.get_tools_param")
    def test_429_retries_five_times_then_raises(self, mock_get_tools, mock_sleep):
        mock_get_tools.return_value = []
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = FakeAPIStatusError(429)

        with pytest.raises(RuntimeError):
            run_inference(
                conversation=[{"role": "user", "content": "Hello"}],
                llm_client=mock_client,
                tools=[],
            )

        assert mock_client.messages.create.call_count == 5
        assert mock_sleep.call_count == 5

    @patch("time.sleep")
    @patch("agent.tools_utils.get_tools_param")
    def test_529_retries_five_times_then_raises(self, mock_get_tools, mock_sleep):
        mock_get_tools.return_value = []
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = FakeAPIStatusError(529)

        with pytest.raises(RuntimeError):
            run_inference(
                conversation=[{"role": "user", "content": "Hello"}],
                llm_client=mock_client,
                tools=[],
            )

        assert mock_client.messages.create.call_count == 5

    @patch("time.sleep")
    @patch("agent.tools_utils.get_tools_param")
    def test_success_after_transient_failure(self, mock_get_tools, mock_sleep):
        mock_get_tools.return_value = []
        mock_response = _make_mock_response()
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = [
            FakeAPIStatusError(429),
            FakeAPIStatusError(429),
            mock_response,
        ]

        content, tokens = run_inference(
            conversation=[{"role": "user", "content": "Hello"}],
            llm_client=mock_client,
            tools=[],
        )

        assert content == mock_response.content
        assert mock_client.messages.create.call_count == 3

    @patch("time.sleep")
    @patch("agent.tools_utils.get_tools_param")
    def test_non_retryable_error_raises_immediately(self, mock_get_tools, mock_sleep):
        mock_get_tools.return_value = []
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = FakeAPIStatusError(401)

        with pytest.raises(Exception):
            run_inference(
                conversation=[{"role": "user", "content": "Hello"}],
                llm_client=mock_client,
                tools=[],
            )

        # Should not retry for non-retryable errors
        assert mock_client.messages.create.call_count == 1
