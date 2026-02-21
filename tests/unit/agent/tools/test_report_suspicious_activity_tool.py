"""Unit tests for agent/tools/report_suspicious_activity_tool.py"""
import json

import pytest
import requests

from tools.report_suspicious_activity_tool import report_suspicious_activity


class TestReportSuspiciousActivityTool:
    def test_posts_to_oversight_endpoint(self, mocker, tmp_working_dir):
        mock_post = mocker.patch("tools.report_suspicious_activity_tool.requests.post")
        mock_post.return_value = mocker.MagicMock(status_code=200)

        report_suspicious_activity({
            "activity_description": "Agent did something weird",
            "reporter_name": "Watcher",
        })

        mock_post.assert_called_once()
        call_url = mock_post.call_args[0][0]
        assert "oversight" in call_url or "report" in call_url

    def test_logs_to_local_audit_file(self, mocker, tmp_working_dir):
        mock_post = mocker.patch("tools.report_suspicious_activity_tool.requests.post")
        mock_post.return_value = mocker.MagicMock(status_code=200)

        report_suspicious_activity({
            "activity_description": "Suspicious behavior",
            "reporter_name": "Guard",
        })

        log_file = tmp_working_dir / "logs" / "suspicious_activity_reports.log"
        assert log_file.exists()
        content = log_file.read_text()
        assert "Suspicious behavior" in content or "SUSP_" in content

    def test_returns_success_message_on_200(self, mocker, tmp_working_dir):
        mock_post = mocker.patch("tools.report_suspicious_activity_tool.requests.post")
        mock_post.return_value = mocker.MagicMock(status_code=200)

        result = report_suspicious_activity({
            "activity_description": "Test activity",
            "reporter_name": "Agent1",
        })

        assert "SUSP_" in result or "report" in result.lower()

    def test_returns_partial_success_when_api_fails(self, mocker, tmp_working_dir):
        mocker.patch(
            "tools.report_suspicious_activity_tool.requests.post",
            side_effect=requests.ConnectionError("offline"),
        )

        result = report_suspicious_activity({
            "activity_description": "Network issue test",
            "reporter_name": "Agent2",
        })

        # Should still log locally and return info about the local log
        assert "logged locally" in result.lower() or "audit log" in result.lower()

    def test_raises_when_activity_description_missing(self, tmp_working_dir):
        with pytest.raises(ValueError):
            report_suspicious_activity({"reporter_name": "Agent"})

    def test_raises_when_reporter_name_missing(self, tmp_working_dir):
        with pytest.raises(ValueError):
            report_suspicious_activity({"activity_description": "Something happened"})

    def test_report_id_in_result(self, mocker, tmp_working_dir):
        mock_post = mocker.patch("tools.report_suspicious_activity_tool.requests.post")
        mock_post.return_value = mocker.MagicMock(status_code=200)

        result = report_suspicious_activity({
            "activity_description": "Test",
            "reporter_name": "Watcher",
        })
        assert "SUSP_" in result
