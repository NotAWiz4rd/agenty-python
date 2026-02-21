"""
E2E tests for the full multi-agent stack.

These tests require a running Docker stack. Skip them by default; set E2E=1
environment variable to enable.

Usage:
    E2E=1 pytest tests/e2e/ -v
"""
import os

import pytest
import requests

pytestmark = pytest.mark.e2e


@pytest.mark.skipif(not os.getenv("E2E"), reason="Set E2E=1 to run e2e tests")
class TestMultiAgentE2E:
    AGENT_1_URL = os.getenv("AGENT_1_URL", "http://localhost:8081")
    AGENT_2_URL = os.getenv("AGENT_2_URL", "http://localhost:8082")
    GROUP_CHAT_URL = os.getenv("GROUP_CHAT_URL", "http://localhost:5000")

    def test_agent_1_health_returns_200(self):
        r = requests.get(f"{self.AGENT_1_URL}/health", timeout=5)
        assert r.status_code == 200
        assert r.json()["status"] == "healthy"

    def test_agent_2_health_returns_200(self):
        r = requests.get(f"{self.AGENT_2_URL}/health", timeout=5)
        assert r.status_code == 200
        assert r.json()["status"] == "healthy"

    def test_group_chat_health_returns_200(self):
        r = requests.get(f"{self.GROUP_CHAT_URL}/health", timeout=5)
        assert r.status_code == 200

    def test_group_chat_message_count_increments(self):
        r_before = requests.get(f"{self.GROUP_CHAT_URL}/status", timeout=5)
        count_before = r_before.json()["total_messages"]

        requests.post(
            f"{self.GROUP_CHAT_URL}/send",
            json={"username": "e2e_test", "message": "ping"},
            timeout=5,
        )

        r_after = requests.get(f"{self.GROUP_CHAT_URL}/status", timeout=5)
        assert r_after.json()["total_messages"] > count_before

    def test_agent_1_receives_message_within_timeout(self):
        import time

        initial = requests.get(f"{self.AGENT_1_URL}/health", timeout=5).json()["messages_processed"]
        requests.post(
            f"{self.AGENT_1_URL}/send-message",
            json={"message": "e2e test message", "from_agent": "e2e_runner"},
            timeout=5,
        )

        # Poll for up to 10 seconds
        deadline = time.time() + 10
        while time.time() < deadline:
            current = requests.get(f"{self.AGENT_1_URL}/health", timeout=5).json()["messages_processed"]
            if current > initial:
                return
            time.sleep(0.5)

        pytest.fail("Agent 1 did not process the message within 10 seconds")
