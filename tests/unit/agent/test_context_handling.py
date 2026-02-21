"""Unit tests for agent/context_handling.py"""
import pickle
import sys
import threading

import pytest

import context_handling
from context_handling import (
    add_to_message_queue,
    cleanup_context,
    get_all_from_message_queue,
    load_conversation,
)


# ---------------------------------------------------------------------------
# Fixture: drain the global queue before/after each test
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def clear_queue():
    while not context_handling.message_queue.empty():
        context_handling.message_queue.get()
    yield
    while not context_handling.message_queue.empty():
        context_handling.message_queue.get()


@pytest.fixture(autouse=True)
def reset_sys_flags():
    """Remove any leftover sys flags between tests."""
    for flag in ("is_restarting", "is_error_exit"):
        if hasattr(sys, flag):
            delattr(sys, flag)
    yield
    for flag in ("is_restarting", "is_error_exit"):
        if hasattr(sys, flag):
            delattr(sys, flag)


# ---------------------------------------------------------------------------
# add_to_message_queue / get_all_from_message_queue
# ---------------------------------------------------------------------------

class TestMessageQueue:
    def test_single_message_added_and_retrieved(self):
        add_to_message_queue("hello")
        result = get_all_from_message_queue()
        assert result == ["hello"]

    def test_multiple_messages_fifo_order(self):
        for msg in ["a", "b", "c"]:
            add_to_message_queue(msg)
        result = get_all_from_message_queue()
        assert result == ["a", "b", "c"]

    def test_empty_queue_returns_empty_list(self):
        result = get_all_from_message_queue()
        assert result == []

    def test_get_all_clears_the_queue(self):
        add_to_message_queue("msg1")
        get_all_from_message_queue()
        result = get_all_from_message_queue()
        assert result == []

    def test_add_always_returns_true(self):
        assert add_to_message_queue("any") is True

    def test_thread_safety_100_concurrent_writers(self):
        num_writers = 100
        barrier = threading.Barrier(num_writers)

        def writer(i):
            barrier.wait()  # all threads start at once
            add_to_message_queue(f"msg_{i}")

        threads = [threading.Thread(target=writer, args=(i,)) for i in range(num_writers)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        messages = get_all_from_message_queue()
        assert len(messages) == num_writers
        assert set(messages) == {f"msg_{i}" for i in range(num_writers)}


# ---------------------------------------------------------------------------
# load_conversation
# ---------------------------------------------------------------------------

class TestLoadConversation:
    def test_returns_none_when_file_missing(self, tmp_path):
        result = load_conversation(str(tmp_path / "nonexistent.pkl"))
        assert result is None

    def test_returns_deserialized_conversation(self, tmp_path):
        expected = [{"role": "user", "content": "Hello"}]
        pkl_file = tmp_path / "conv.pkl"
        pkl_file.write_bytes(pickle.dumps(expected))

        result = load_conversation(str(pkl_file))
        assert result == expected

    def test_load_complex_conversation(self, tmp_path):
        expected = [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello!"},
            {"role": "user", "content": "How are you?"},
        ]
        pkl_file = tmp_path / "conv.pkl"
        pkl_file.write_bytes(pickle.dumps(expected))

        result = load_conversation(str(pkl_file))
        assert result == expected


# ---------------------------------------------------------------------------
# cleanup_context
# ---------------------------------------------------------------------------

class TestCleanupContext:
    def test_deletes_context_file(self, tmp_working_dir):
        ctx_file = tmp_working_dir / "conversation_context.pkl"
        ctx_file.write_bytes(b"data")

        cleanup_context()

        assert not ctx_file.exists()

    def test_noop_when_file_missing(self, tmp_working_dir):
        # Should not raise when file doesn't exist
        cleanup_context()

    def test_skipped_when_is_restarting_true(self, tmp_working_dir):
        ctx_file = tmp_working_dir / "conversation_context.pkl"
        ctx_file.write_bytes(b"data")

        sys.is_restarting = True
        cleanup_context()

        assert ctx_file.exists()  # file should NOT have been deleted

    def test_skipped_when_is_error_exit_true(self, tmp_working_dir):
        ctx_file = tmp_working_dir / "conversation_context.pkl"
        ctx_file.write_bytes(b"data")

        sys.is_error_exit = True
        cleanup_context()

        assert ctx_file.exists()  # file should NOT have been deleted
