"""
Shared fixtures and path setup for the agenty-python test suite.
"""
import json
import os
import sys

import pytest

# --- Set a fake API key before any module imports that need it ---
os.environ.setdefault("ANTHROPIC_API_KEY", "sk-ant-test-key-for-testing-only")

# --- Add source directories to sys.path ---
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_HERE)

for _dir in [
    _REPO_ROOT,                                       # for `from agent.tools_utils import ...`
    os.path.join(_REPO_ROOT, "agent"),                # for `from tools import ...`, `from util import ...`
    os.path.join(_REPO_ROOT, "group_chat"),
    os.path.join(_REPO_ROOT, "oversight_officer"),
    os.path.join(_REPO_ROOT, "group_work_log"),
]:
    if _dir not in sys.path:
        sys.path.insert(0, _dir)


# ---------------------------------------------------------------------------
# Shared test data
# ---------------------------------------------------------------------------

SAMPLE_TEAM_CONFIG = {
    "task": "Test task",
    "agents": [
        {"name": "Claude", "host": "http://0.0.0.0", "port": 8081, "isCurrentAgent": True},
        {"name": "Carmen", "host": "http://0.0.0.0", "port": 8082, "isCurrentAgent": False},
    ],
}


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def team_config_file(tmp_path):
    """Write a minimal team-config.json to a temp directory and return the path."""
    f = tmp_path / "team-config.json"
    f.write_text(json.dumps(SAMPLE_TEAM_CONFIG))
    return f


@pytest.fixture
def conversation():
    """Minimal valid conversation list."""
    return [{"role": "user", "content": "Hello"}]


@pytest.fixture
def tmp_working_dir(tmp_path, monkeypatch):
    """Run tests from an isolated temp directory."""
    monkeypatch.chdir(tmp_path)
    return tmp_path
