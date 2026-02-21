"""Unit tests for group_work_log/group_work_log.py"""
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

import group_work_log.group_work_log as group_work_log
from group_work_log.group_work_log import app, extract_assistant_actions


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_llm(mocker):
    """Mock the Anthropic client so no real API calls are made."""
    mock_resp = MagicMock()
    mock_resp.content = [MagicMock(text="• Did thing A\n• Used tool B\n• Got result C")]
    mocker.patch.object(group_work_log.claude_client.messages, "create", return_value=mock_resp)
    return mock_resp


@pytest.fixture
def client(tmp_working_dir, mock_llm):
    """TestClient with fresh state per test."""
    group_work_log.summaries.clear()
    monkeypatch_attr = group_work_log.SUMMARY_FILE
    group_work_log.SUMMARY_FILE = str(tmp_working_dir / "summaries.txt")
    with TestClient(app) as c:
        yield c
    group_work_log.summaries.clear()
    group_work_log.SUMMARY_FILE = monkeypatch_attr


_SAMPLE_MESSAGES = [
    {
        "role": "assistant",
        "content": [{"type": "text", "text": "I completed the task."}],
    }
]

_WORKLOG_PAYLOAD = {
    "agent_name": "TestAgent",
    "first_timestamp": "2024-01-01T00:00:00",
    "last_timestamp": "2024-01-01T01:00:00",
    "messages": _SAMPLE_MESSAGES,
}


# ---------------------------------------------------------------------------
# POST /submit-worklog
# ---------------------------------------------------------------------------

class TestSubmitWorklog:
    def test_returns_200(self, client):
        r = client.post("/submit-worklog", json=_WORKLOG_PAYLOAD)
        assert r.status_code == 200

    def test_response_has_ok_status(self, client):
        r = client.post("/submit-worklog", json=_WORKLOG_PAYLOAD)
        assert r.json()["status"] == "ok"

    def test_response_has_summary_created_true(self, client):
        r = client.post("/submit-worklog", json=_WORKLOG_PAYLOAD)
        assert r.json()["summary_created"] is True

    def test_summary_appears_in_get_summaries(self, client):
        client.post("/submit-worklog", json=_WORKLOG_PAYLOAD)
        r = client.get("/summaries")
        assert r.status_code == 200
        assert len(r.json()) == 1

    def test_returns_400_for_missing_agent_name(self, client):
        payload = {**_WORKLOG_PAYLOAD, "agent_name": ""}
        r = client.post("/submit-worklog", json=payload)
        assert r.status_code == 400

    def test_returns_400_for_empty_messages(self, client):
        payload = {**_WORKLOG_PAYLOAD, "messages": []}
        r = client.post("/submit-worklog", json=payload)
        assert r.status_code == 400

    def test_persists_to_file(self, client, tmp_working_dir):
        client.post("/submit-worklog", json=_WORKLOG_PAYLOAD)
        summary_file = tmp_working_dir / "summaries.txt"
        assert summary_file.exists()
        content = summary_file.read_text()
        assert "TestAgent" in content


# ---------------------------------------------------------------------------
# GET /summaries
# ---------------------------------------------------------------------------

class TestGetSummaries:
    def test_returns_all_summaries(self, client):
        client.post("/submit-worklog", json=_WORKLOG_PAYLOAD)
        client.post("/submit-worklog", json={**_WORKLOG_PAYLOAD, "agent_name": "AgentB"})
        r = client.get("/summaries")
        assert len(r.json()) == 2

    def test_returns_empty_list_initially(self, client):
        r = client.get("/summaries")
        assert r.json() == []

    def test_after_timestamp_filters_older_entries(self, client):
        client.post("/submit-worklog", json=_WORKLOG_PAYLOAD)
        import time
        from datetime import datetime, timezone
        time.sleep(0.01)
        # Always include microseconds to satisfy server-side strptime validation
        cutoff = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")
        time.sleep(0.01)
        client.post("/submit-worklog", json={**_WORKLOG_PAYLOAD, "agent_name": "AgentB"})
        r = client.get(f"/summaries?after_timestamp={cutoff}")
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 1

    def test_returns_400_for_invalid_timestamp(self, client):
        r = client.get("/summaries?after_timestamp=not-a-date")
        assert r.status_code == 400


# ---------------------------------------------------------------------------
# extract_assistant_actions
# ---------------------------------------------------------------------------

class TestExtractAssistantActions:
    def test_extracts_text_from_assistant_message(self):
        messages = [
            {"role": "assistant", "content": [{"type": "text", "text": "I did something"}]}
        ]
        result = extract_assistant_actions(messages)
        assert "I did something" in result

    def test_extracts_tool_use_from_assistant_message(self):
        messages = [
            {
                "role": "assistant",
                "content": [
                    {"type": "tool_use", "name": "read_file", "input": {"path": "test.txt"}}
                ],
            }
        ]
        result = extract_assistant_actions(messages)
        assert "read_file" in result

    def test_handles_string_content(self):
        messages = [
            {"role": "assistant", "content": "Plain text response"}
        ]
        result = extract_assistant_actions(messages)
        assert "Plain text response" in result

    def test_returns_empty_string_for_empty_input(self):
        result = extract_assistant_actions([])
        assert result == ""

    def test_includes_all_messages(self):
        messages = [
            {"role": "assistant", "content": [{"type": "text", "text": "First action"}]},
            {"role": "assistant", "content": [{"type": "text", "text": "Second action"}]},
        ]
        result = extract_assistant_actions(messages)
        assert "First action" in result
        assert "Second action" in result
