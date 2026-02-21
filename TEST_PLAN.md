# Pytest Test Plan — Agenty

## Overview

This document describes the planned test suite for the agenty-python repository. The system has no existing tests. The plan prioritises the agent core and works outward to the auxiliary services.

Tests are organised into three tiers:

| Tier | Description | External Deps |
|------|-------------|---------------|
| Unit | Pure logic, isolated with mocks | None |
| Integration | Multiple modules together, still mocked at boundaries | None / minimal |
| E2E | Full service stack via real HTTP | Docker / network |

Start with unit and integration tests. E2E tests are optional and require a running stack.

---

## Test Infrastructure

### Directory Layout

```
tests/
├── conftest.py                   # Shared fixtures
├── unit/
│   ├── agent/
│   │   ├── test_llm.py
│   │   ├── test_context_handling.py
│   │   ├── test_tools_utils.py
│   │   ├── test_team_config_loader.py
│   │   ├── test_util.py
│   │   └── tools/
│   │       ├── test_read_file_tool.py
│   │       ├── test_edit_file_tool.py
│   │       ├── test_delete_file_tool.py
│   │       ├── test_list_files_tool.py
│   │       ├── test_command_tool.py
│   │       ├── test_task_tracker_tool.py
│   │       ├── test_wait_tool.py
│   │       ├── test_send_group_message_tool.py
│   │       ├── test_send_agent_message_tool.py
│   │       └── test_report_suspicious_activity_tool.py
│   ├── group_chat/
│   │   └── test_group_chat.py
│   ├── oversight_officer/
│   │   └── test_activity_check.py
│   └── group_work_log/
│       └── test_group_work_log.py
├── integration/
│   ├── test_tool_pipeline.py
│   ├── test_context_save_restore.py
│   ├── test_agent_api.py
│   ├── test_group_chat_api.py
│   └── test_message_queue.py
└── e2e/                          # Optional — requires Docker stack
    └── test_multi_agent.py
```

### Dependencies to Add

```
# requirements-dev.txt (create this file)
pytest>=8.0
pytest-asyncio>=0.23
pytest-httpserver>=1.0
pytest-mock>=3.12
pyfakefs>=5.3
httpx>=0.28.1   # already in requirements.txt, needed here for TestClient
```

### pytest Configuration

Add to `pyproject.toml` (or `pytest.ini`):

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
markers = [
    "unit: fast, isolated tests",
    "integration: multi-module tests with mocked boundaries",
    "e2e: full stack tests requiring Docker",
]
```

### Shared Fixtures (`tests/conftest.py`)

```python
import json
import pytest
from pathlib import Path

SAMPLE_TEAM_CONFIG = {
    "task": "Test task",
    "agents": [
        {"name": "Claude", "host": "http://0.0.0.0", "port": 8081, "isCurrentAgent": True},
        {"name": "Carmen", "host": "http://0.0.0.0", "port": 8082, "isCurrentAgent": False},
    ],
}

@pytest.fixture
def team_config_file(tmp_path):
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
```

---

## Unit Tests

### `agent/llm.py`

**File:** `tests/unit/agent/test_llm.py`

#### `get_system_prompt(agent_name, is_team_mode)`
- Returns a non-empty string in single-agent mode.
- Returns a string containing the agent name in team mode.
- Does not contain team-specific instructions in single-agent mode.
- Contains team-specific instructions in team mode.

#### `remove_all_but_last_three_cache_controls(conversation)`
- Conversation with 0 cache controls is returned unchanged.
- Conversation with exactly 3 cache controls is returned unchanged.
- Conversation with 5 cache controls retains only the last 3 (the 2 earlier ones are stripped).
- Does not mutate the original list.

#### `run_inference(...)` (mocked)
- On success: returns `(content, token_usage)`.
- On `429` error: retries up to 5 times before raising.
- On `529` error: retries up to 5 times before raising.
- On success after transient failure: returns normally.
- Inserts `ask_human` tool when consecutive tool count exceeds limit (mock client responses).

---

### `agent/context_handling.py`

**File:** `tests/unit/agent/test_context_handling.py`

#### `add_to_message_queue(message)` / `get_all_from_message_queue()`
- Single message added and retrieved correctly.
- Multiple messages retrieved in FIFO order.
- `get_all_from_message_queue()` returns empty list when queue is empty.
- `get_all_from_message_queue()` clears the queue.
- Thread-safety: 100 concurrent writers, all messages present after join.

#### `load_conversation(save_file)` / `cleanup_context()`
- Returns `None` when file does not exist.
- Returns deserialized conversation when file exists.
- `cleanup_context()` deletes the file.
- `cleanup_context()` is a no-op when file does not exist.
- Context file is not deleted when `sys.is_error_exit` is `True`.

---

### `agent/tools_utils.py`

**File:** `tests/unit/agent/test_tools_utils.py`

#### `get_tool_list(is_team_mode)`
- Non-team mode: `send_group_message`, `send_agent_message`, `wait`, `report_suspicious_activity` are absent.
- Team mode: those four tools are present.
- All returned items are `ToolDefinition` instances.
- No duplicate tool names in either mode.

#### `execute_tool(tools, tool_name, input_data)`
- Calls the matching tool function with the given input.
- Returns the function's return value.
- Returns an error string when tool name does not exist.
- Returns an error string (not an exception) when the tool function raises.

#### `deal_with_tool_results(tool_results, conversation)`
- Returns `False` when no restart signal is present.
- Returns `True` and sets restart flag when `{"restart": true}` is in results.
- Calls `reset_context` path when `{"restart": true, "reset_context": true}` is in results.

---

### `agent/team_config_loader.py`

**File:** `tests/unit/agent/test_team_config_loader.py`

#### `load_team_config(path)`
- Parses valid JSON and returns a `TeamConfig` object.
- Raises `FileNotFoundError` for a missing file.
- Raises `ValueError` (or similar) for malformed JSON.
- `TeamConfig.get_current_agent()` returns the agent with `isCurrentAgent: True`.
- `TeamConfig.get_current_agent()` raises when no agent is marked current.

#### `get_agent_endpoints(team_config)`
- Returns only endpoints for agents that are not the current agent.
- Constructs URL correctly as `{host}:{port}`.

#### Docker mode overrides (`--docker_agent_index`)
- With `docker_agent_index=0`, `isCurrentAgent` is set on the agent at index 0.
- Agent name and port are taken from config at that index.

---

### `agent/util.py`

**File:** `tests/unit/agent/test_util.py`

#### `get_agent_turn_delay_in_ms(number_of_agents)`
- Returns 0 for 1 agent.
- Returns `(n - 1) * 2000` for n agents.

#### `log_error(message)` (with mocked file I/O)
- Writes the message to `error.txt`.
- Appends when file already exists (does not truncate).

#### `get_new_messages_from_group_chat(...)` (with mocked `requests`)
- Returns parsed messages on HTTP 200.
- Returns empty list on connection error.

---

### Tools

#### `read_file_tool.py` — `tests/unit/agent/tools/test_read_file_tool.py`

All tests use `tmp_working_dir` fixture or `pyfakefs`.

- Reads content of an existing file and returns it.
- Returns an error message for a non-existent file.
- Rejects paths outside the working directory (path traversal: `../../etc/passwd`).
- Returns an error for a path that is a directory.

#### `edit_file_tool.py` — `tests/unit/agent/tools/test_edit_file_tool.py`

- Creates a new file when it does not exist.
- Overwrites the content of an existing file.
- Returns a success message on write.
- Returns an error when the path is a directory.
- Creates parent directories if they don't exist.

#### `delete_file_tool.py` — `tests/unit/agent/tools/test_delete_file_tool.py`

- Deletes an existing file and returns success.
- Returns an error for a non-existent file.
- Refuses to delete a directory (should require a file path).

#### `list_files_tool.py` — `tests/unit/agent/tools/test_list_files_tool.py`

- Lists files in a populated directory.
- Returns an empty result for an empty directory.
- Returns an error for a non-existent directory.
- Respects gitignore / exclusion rules if implemented.

#### `command_tool.py` — `tests/unit/agent/tools/test_command_tool.py`

All subprocess calls mocked with `pytest-mock`.

- Runs a simple command and returns stdout.
- Returns stderr content when command fails.
- Rejects blacklisted commands (e.g. `rm -rf /`).
- Kills a running process when stop is requested.
- Long-running command output is truncated at 1000 lines.

#### `task_tracker_tool.py` — `tests/unit/agent/tools/test_task_tracker_tool.py`

Uses `tmp_working_dir`.

- Creates a new task tracker file on first use.
- Adds a task and reads it back.
- Marks a task as complete.
- Returns all tasks when listing.
- File format is valid JSON throughout.

#### `wait_tool.py` — `tests/unit/agent/tools/test_wait_tool.py`

- Calls `time.sleep` with the correct number of seconds (mock `time.sleep`).
- Returns a confirmation message.
- Rejects negative durations.

#### `send_group_message_tool.py` — `tests/unit/agent/tools/test_send_group_message_tool.py`

Mock `requests.post`.

- POSTs message to the configured group chat endpoint.
- Returns success message on HTTP 200.
- Returns error message on connection failure.
- Returns error message on non-200 status.

#### `send_agent_message_tool.py` — `tests/unit/agent/tools/test_send_agent_message_tool.py`

Mock `requests.post`.

- POSTs message to the correct agent URL derived from team config.
- Returns success on HTTP 200.
- Returns error when target agent name is not in config.
- Returns error on connection timeout.

#### `report_suspicious_activity_tool.py` — `tests/unit/agent/tools/test_report_suspicious_activity_tool.py`

Mock `requests.post` and file I/O.

- POSTs report to the oversight officer endpoint.
- Logs the report to the local file.
- Returns success on HTTP 200.
- Returns partial success when HTTP fails but local file write succeeds.

---

### `group_chat/group_chat.py`

**File:** `tests/unit/group_chat/test_group_chat.py`

Use FastAPI `TestClient`.

#### `GET /health`
- Returns `200` with `status: ok`.

#### `GET /status`
- Returns total message count and uptime.

#### `POST /send`
- Accepts `{"username": "Alice", "message": "Hello"}` and returns `200`.
- Persists message to `chat_messages.txt` in format `username||timestamp||message`.
- Rejects missing fields with `422`.

#### `GET /messages`
- Returns all messages when no `after` parameter.
- Returns only messages after the given timestamp when `after` is provided.
- Returns empty list when no messages match.

#### Thread safety
- 50 concurrent POST `/send` requests all land in the file without corruption.

---

### `oversight_officer/activity_check.py`

**File:** `tests/unit/oversight_officer/test_activity_check.py`

#### `extract_severity_level(llm_response_text)`
- Returns `"low"`, `"medium"`, or `"high"` from well-formed text.
- Returns a default (e.g. `"unknown"`) from text that has no level marker.
- Case-insensitive matching.

#### Severity evaluation (mock LLM client)
- Calls LLM with the agent's recent actions.
- Parses LLM response and returns severity.
- Logs severity to the activity log file.

---

### `group_work_log/group_work_log.py`

**File:** `tests/unit/group_work_log/test_group_work_log.py`

Use FastAPI `TestClient`.

#### `POST /submit`
- Accepts work log entry with agent name, timestamp, and text.
- Persists entry to the log file.
- Returns `200` on success.

#### `GET /summary`
- Returns aggregated summary of all entries.
- Returns entries filtered by time range when `since` parameter provided.

#### `extract_assistant_actions(messages)`
- Extracts only assistant-role messages from a conversation list.
- Skips tool-use messages.
- Returns empty list for empty input.

---

## Integration Tests

### `test_tool_pipeline.py`

Test the full tool registration → execution path.

- `get_tool_list(False)` produces tools whose `function` references resolve and can be called.
- `execute_tool` finds and runs `read_file` against a real temp file.
- `execute_tool` propagates error strings when the tool raises.
- `deal_with_tool_results` triggers restart detection across the full pipeline.

### `test_context_save_restore.py`

- Save a conversation to a temp pickle file.
- Reload it in a fresh call to `load_conversation()`.
- Verify the reloaded conversation matches the original.
- Verify cleanup removes the file.

### `test_agent_api.py`

Start the FastAPI app from `agent/api.py` in-process using `TestClient`.

- `GET /health` returns 200 with uptime and message count.
- `GET /status` returns agent metadata.
- `POST /send-message` adds a message to the queue; verify via `get_all_from_message_queue()`.
- Multiple `POST /send-message` requests arrive in queue in order.

### `test_group_chat_api.py`

Start the group chat FastAPI app in-process using `TestClient`.

- Full send-then-retrieve round-trip.
- `after` timestamp filtering returns only newer messages.
- `/status` count increments with each send.

### `test_message_queue.py`

- Simulate the API endpoint calling `add_to_message_queue()` from multiple threads while the agent loop calls `get_all_from_message_queue()` — no messages lost.
- Queue is empty after a full drain cycle.

---

## E2E Tests (Optional)

**File:** `tests/e2e/test_multi_agent.py`

These tests require the full Docker stack to be running. Mark with `@pytest.mark.e2e` and skip by default.

```python
@pytest.mark.e2e
@pytest.mark.skipif(not os.getenv("E2E"), reason="Set E2E=1 to run")
```

### Scenarios

- Agent 1 sends a group message; Agent 2 receives it within 10 seconds.
- Health endpoints on all agents return 200.
- Group chat `/status` shows message count increasing after agents communicate.
- Oversight officer flags a message with severity above threshold.

---

## What Not to Test

| Item | Reason |
|------|---------|
| `Agent.run()` main loop | Infinite loop; test helper functions directly |
| `restart_program_tool` / `graceful_shutdown_tool` | Call `os.execv` / `os._exit`; would kill the test runner |
| Interactive `ask_human` stdin path | Requires a human; test everything around it |
| LLM responses end-to-end | Requires API key and network; mock the client instead |
| Docker/deployment scripts | Shell scripts; out of scope for pytest |

---

## Mocking Strategy Summary

| Dependency | Mock approach |
|------------|--------------|
| Anthropic client | `pytest-mock` `mocker.patch` on `anthropic.Anthropic` |
| File system | `pyfakefs` `fs` fixture or `tmp_path` |
| HTTP requests (`requests`) | `pytest-mock` or `responses` library |
| `time.sleep` | `mocker.patch("time.sleep")` |
| `subprocess.Popen` | `mocker.patch("subprocess.Popen")` |
| FastAPI apps | `httpx.AsyncClient` / `TestClient` |
| `os.execv` / `os._exit` | `mocker.patch("os.execv")`, `mocker.patch("os._exit")` |

---

## Running Tests

```bash
# Install dev deps
pip install -r requirements-dev.txt

# All unit tests
pytest tests/unit/ -v

# All integration tests
pytest tests/integration/ -v

# Everything except E2E
pytest tests/ -v -m "not e2e"

# With coverage
pytest tests/ --cov=agent --cov=group_chat --cov=oversight_officer \
    --cov=group_work_log --cov-report=term-missing

# E2E (requires running stack)
E2E=1 pytest tests/e2e/ -v
```

---

## Coverage Goals

| Module | Target |
|--------|--------|
| `agent/llm.py` | 80% |
| `agent/context_handling.py` | 90% |
| `agent/tools_utils.py` | 90% |
| `agent/team_config_loader.py` | 95% |
| `agent/util.py` | 85% |
| `agent/tools/*.py` | 75% each |
| `group_chat/group_chat.py` | 85% |
| `oversight_officer/activity_check.py` | 80% |
| `group_work_log/group_work_log.py` | 80% |
