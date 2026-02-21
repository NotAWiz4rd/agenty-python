"""Unit tests for oversight_officer/activity_check.py"""
from unittest.mock import MagicMock

import pytest

import activity_check
from activity_check import add_to_activity_log, check_activity, extract_severity_level


# ---------------------------------------------------------------------------
# extract_severity_level
# ---------------------------------------------------------------------------

class TestExtractSeverityLevel:
    def test_returns_critical(self):
        assert extract_severity_level("This is a CRITICAL issue") == "CRITICAL"

    def test_returns_high(self):
        assert extract_severity_level("Severity: HIGH - dangerous behavior") == "HIGH"

    def test_returns_medium(self):
        assert extract_severity_level("Evaluated as MEDIUM risk") == "MEDIUM"

    def test_returns_low(self):
        assert extract_severity_level("Risk level: LOW - not concerning") == "LOW"

    def test_returns_unknown_for_no_marker(self):
        assert extract_severity_level("Nothing suspicious here") == "UNKNOWN"

    def test_critical_takes_priority_over_high(self):
        # If both appear, CRITICAL is checked first
        result = extract_severity_level("CRITICAL and HIGH levels detected")
        assert result == "CRITICAL"

    def test_case_sensitive_lowercase_not_matched(self):
        # The function checks for uppercase only
        assert extract_severity_level("this is critical") == "UNKNOWN"
        assert extract_severity_level("this is high risk") == "UNKNOWN"

    def test_returns_unknown_for_empty_string(self):
        assert extract_severity_level("") == "UNKNOWN"


# ---------------------------------------------------------------------------
# check_activity (with mocked LLM client)
# ---------------------------------------------------------------------------

class TestCheckActivity:
    def _make_mock_response(self, severity: str):
        mock_content = MagicMock()
        mock_content.text = f"Severity level: {severity}. Analysis complete."
        mock_content.model_dump_json.return_value = f'{{"text": "Severity: {severity}"}}'

        mock_response = MagicMock()
        mock_response.content = [mock_content]
        return mock_response

    def test_calls_llm_with_activity_text(self, mocker, tmp_working_dir):
        mock_create = mocker.patch.object(
            activity_check.client.messages, "create",
            return_value=self._make_mock_response("LOW"),
        )
        check_activity("Agent ran a command")
        mock_create.assert_called_once()
        call_kwargs = mock_create.call_args[1]
        # The messages should contain the activity text
        messages = call_kwargs.get("messages", [])
        assert any("Agent ran a command" in str(m) for m in messages)

    def test_logs_to_activity_file(self, mocker, tmp_working_dir):
        mocker.patch.object(
            activity_check.client.messages, "create",
            return_value=self._make_mock_response("LOW"),
        )
        check_activity("Normal activity log test")
        log_file = tmp_working_dir / "logs" / "suspicious_activity_reports.log"
        assert log_file.exists()

    def test_parses_severity_from_llm_response(self, mocker, tmp_working_dir):
        mocker.patch.object(
            activity_check.client.messages, "create",
            return_value=self._make_mock_response("HIGH"),
        )
        # Should not raise; severity should be parsed correctly
        check_activity("Potentially dangerous action")

    def test_handles_critical_severity(self, mocker, tmp_working_dir, capsys):
        mocker.patch.object(
            activity_check.client.messages, "create",
            return_value=self._make_mock_response("CRITICAL"),
        )
        check_activity("Critical behavior detected")
        captured = capsys.readouterr()
        assert "CRITICAL" in captured.out


# ---------------------------------------------------------------------------
# add_to_activity_log
# ---------------------------------------------------------------------------

class TestAddToActivityLog:
    def test_creates_log_file(self, tmp_working_dir):
        add_to_activity_log('{"test": true}')
        log_file = tmp_working_dir / "logs" / "suspicious_activity_reports.log"
        assert log_file.exists()

    def test_appends_to_log_file(self, tmp_working_dir):
        add_to_activity_log("entry1")
        add_to_activity_log("entry2")
        content = (tmp_working_dir / "logs" / "suspicious_activity_reports.log").read_text()
        assert "entry1" in content
        assert "entry2" in content
