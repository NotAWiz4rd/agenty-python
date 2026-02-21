"""Integration tests for agent/api.py FastAPI app."""
import pytest
from fastapi.testclient import TestClient

import api
import context_handling
from api import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_api_state():
    """Reset message counter and drain message queue between tests."""
    api.message_count = 0
    while not context_handling.message_queue.empty():
        context_handling.message_queue.get()
    yield
    api.message_count = 0
    while not context_handling.message_queue.empty():
        context_handling.message_queue.get()


class TestHealthEndpoint:
    def test_returns_200(self):
        r = client.get("/health")
        assert r.status_code == 200

    def test_status_is_healthy(self):
        r = client.get("/health")
        assert r.json()["status"] == "healthy"

    def test_includes_uptime_seconds(self):
        r = client.get("/health")
        assert "uptime_seconds" in r.json()

    def test_includes_messages_processed(self):
        r = client.get("/health")
        assert "messages_processed" in r.json()


class TestStatusEndpoint:
    def test_returns_200(self):
        r = client.get("/status")
        assert r.status_code == 200

    def test_includes_agent_name(self):
        r = client.get("/status")
        assert "agent_name" in r.json()

    def test_includes_status_running(self):
        r = client.get("/status")
        assert r.json()["status"] == "running"


class TestSendMessageEndpoint:
    def test_returns_200(self):
        r = client.post("/send-message", json={"message": "hello", "from_agent": "Bob"})
        assert r.status_code == 200

    def test_response_has_queued_status(self):
        r = client.post("/send-message", json={"message": "hello", "from_agent": "Bob"})
        data = r.json()
        assert data["status"] in ("queued", "sent")

    def test_message_added_to_queue(self):
        client.post("/send-message", json={"message": "test message", "from_agent": "Alice"})
        msgs = context_handling.get_all_from_message_queue()
        assert any("test message" in m for m in msgs)

    def test_sender_name_in_queued_message(self):
        client.post("/send-message", json={"message": "hi", "from_agent": "Carol"})
        msgs = context_handling.get_all_from_message_queue()
        assert any("Carol" in m for m in msgs)

    def test_multiple_messages_arrive_in_queue(self):
        for i in range(5):
            client.post("/send-message", json={"message": f"msg{i}", "from_agent": "Agent"})
        msgs = context_handling.get_all_from_message_queue()
        assert len(msgs) == 5

    def test_rejects_missing_message_field(self):
        r = client.post("/send-message", json={"from_agent": "X"})
        assert r.status_code == 422

    def test_rejects_missing_from_agent_field(self):
        r = client.post("/send-message", json={"message": "hi"})
        assert r.status_code == 422
