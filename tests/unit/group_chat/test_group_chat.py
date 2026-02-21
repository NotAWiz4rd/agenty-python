"""Unit tests for group_chat/group_chat.py"""
import concurrent.futures
import threading

import pytest
from fastapi.testclient import TestClient

import group_chat.group_chat as gc
from group_chat.group_chat import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_group_chat_state(tmp_path, monkeypatch):
    """Reset in-memory state and redirect file writes to tmp_path before each test."""
    gc.messages.clear()
    gc.message_count = 0
    monkeypatch.setattr(gc, "MSG_FILE", str(tmp_path / "chat_messages.txt"))
    yield
    gc.messages.clear()
    gc.message_count = 0


# ---------------------------------------------------------------------------
# GET /health
# ---------------------------------------------------------------------------

class TestHealth:
    def test_returns_200(self):
        r = client.get("/health")
        assert r.status_code == 200

    def test_status_is_healthy(self):
        r = client.get("/health")
        assert r.json()["status"] == "healthy"

    def test_includes_uptime(self):
        r = client.get("/health")
        assert "uptime_seconds" in r.json()

    def test_includes_total_messages(self):
        r = client.get("/health")
        assert "total_messages" in r.json()


# ---------------------------------------------------------------------------
# GET /status
# ---------------------------------------------------------------------------

class TestStatus:
    def test_returns_200(self):
        r = client.get("/status")
        assert r.status_code == 200

    def test_includes_total_messages_count(self):
        r = client.get("/status")
        assert "total_messages" in r.json()

    def test_message_count_reflects_sends(self):
        client.post("/send", json={"username": "Alice", "message": "hi"})
        r = client.get("/status")
        assert r.json()["total_messages"] >= 1


# ---------------------------------------------------------------------------
# POST /send
# ---------------------------------------------------------------------------

class TestSend:
    def test_returns_200_with_ok_status(self):
        r = client.post("/send", json={"username": "Alice", "message": "Hello"})
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

    def test_message_appears_in_memory_store(self):
        client.post("/send", json={"username": "Bob", "message": "World"})
        msgs = [m for m in gc.messages if m.username == "Bob"]
        assert len(msgs) == 1
        assert msgs[0].message == "World"

    def test_message_persisted_to_file(self, tmp_path):
        client.post("/send", json={"username": "Charlie", "message": "Stored"})
        msg_file = tmp_path / "chat_messages.txt"
        assert msg_file.exists()
        content = msg_file.read_text()
        assert "Charlie" in content
        assert "Stored" in content

    def test_file_format_is_pipe_separated(self, tmp_path):
        client.post("/send", json={"username": "Dave", "message": "Test"})
        lines = (tmp_path / "chat_messages.txt").read_text().splitlines()
        parts = lines[0].split("||")
        assert len(parts) == 3
        assert parts[0] == "Dave"

    def test_rejects_missing_username_with_422(self):
        r = client.post("/send", json={"message": "no username"})
        assert r.status_code == 422

    def test_rejects_missing_message_with_422(self):
        r = client.post("/send", json={"username": "Eve"})
        assert r.status_code == 422


# ---------------------------------------------------------------------------
# GET /messages
# ---------------------------------------------------------------------------

class TestGetMessages:
    def test_returns_all_messages(self):
        client.post("/send", json={"username": "A", "message": "msg1"})
        client.post("/send", json={"username": "B", "message": "msg2"})
        r = client.get("/messages")
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 2

    def test_returns_empty_list_when_no_messages(self):
        r = client.get("/messages")
        assert r.status_code == 200
        assert r.json() == []

    def test_message_has_required_fields(self):
        client.post("/send", json={"username": "Frank", "message": "hello"})
        r = client.get("/messages")
        msg = r.json()[0]
        assert "username" in msg
        assert "message" in msg
        assert "timestamp" in msg


# ---------------------------------------------------------------------------
# Thread safety
# ---------------------------------------------------------------------------

class TestThreadSafety:
    def test_concurrent_sends_all_land_in_store(self):
        num_requests = 20

        def send(i):
            return client.post("/send", json={"username": f"user{i}", "message": f"msg{i}"})

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
            futures = [pool.submit(send, i) for i in range(num_requests)]
            results = [f.result() for f in futures]

        assert all(r.status_code == 200 for r in results)
        assert len(gc.messages) == num_requests
