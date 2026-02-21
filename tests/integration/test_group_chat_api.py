"""Integration tests: full group_chat API send-retrieve cycle."""
import pytest
from fastapi.testclient import TestClient

import group_chat.group_chat as gc
from group_chat.group_chat import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_state(tmp_path, monkeypatch):
    gc.messages.clear()
    gc.message_count = 0
    monkeypatch.setattr(gc, "MSG_FILE", str(tmp_path / "chat_messages.txt"))
    yield
    gc.messages.clear()
    gc.message_count = 0


class TestGroupChatApiIntegration:
    def test_send_then_retrieve_round_trip(self):
        client.post("/send", json={"username": "Alice", "message": "hello!"})
        r = client.get("/messages")
        assert r.status_code == 200
        messages = r.json()
        assert len(messages) == 1
        assert messages[0]["username"] == "Alice"
        assert messages[0]["message"] == "hello!"

    def test_multiple_send_then_retrieve(self):
        payloads = [
            {"username": "Alice", "message": "first"},
            {"username": "Bob", "message": "second"},
            {"username": "Alice", "message": "third"},
        ]
        for p in payloads:
            client.post("/send", json=p)

        r = client.get("/messages")
        messages = r.json()
        assert len(messages) == 3
        assert messages[0]["username"] == "Alice"
        assert messages[1]["username"] == "Bob"

    def test_status_count_increments_with_each_send(self):
        r0 = client.get("/status")
        initial = r0.json()["total_messages"]

        client.post("/send", json={"username": "X", "message": "msg1"})
        client.post("/send", json={"username": "X", "message": "msg2"})

        r1 = client.get("/status")
        assert r1.json()["total_messages"] == initial + 2

    def test_messages_include_timestamp(self):
        client.post("/send", json={"username": "Alice", "message": "ts test"})
        r = client.get("/messages")
        msg = r.json()[0]
        assert "timestamp" in msg
        assert msg["timestamp"]  # non-empty

    def test_retrieved_messages_match_sent_order(self):
        for i in range(5):
            client.post("/send", json={"username": "User", "message": f"msg{i}"})
        r = client.get("/messages")
        retrieved = [m["message"] for m in r.json()]
        assert retrieved == [f"msg{i}" for i in range(5)]
