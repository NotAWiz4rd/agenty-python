"""Integration tests: context save and restore cycle."""
import pickle

import pytest

from context_handling import cleanup_context, load_conversation
from util import save_conversation


class TestContextSaveRestore:
    def test_save_and_reload_conversation(self, tmp_working_dir):
        conv = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]
        save_file = str(tmp_working_dir / "context.pkl")
        save_conversation(conv, save_file)
        loaded = load_conversation(save_file)
        assert loaded == conv

    def test_reloaded_conversation_matches_original(self, tmp_working_dir):
        original = [
            {"role": "user", "content": "Task start"},
            {"role": "assistant", "content": [{"type": "text", "text": "Working..."}]},
            {"role": "user", "content": "Continue"},
        ]
        save_file = str(tmp_working_dir / "conv.pkl")
        save_conversation(original, save_file)
        restored = load_conversation(save_file)
        assert restored == original
        assert len(restored) == 3

    def test_save_returns_true_on_success(self, tmp_working_dir):
        conv = [{"role": "user", "content": "test"}]
        result = save_conversation(conv, str(tmp_working_dir / "out.pkl"))
        assert result is True

    def test_save_returns_false_on_failure(self, tmp_working_dir):
        # Try to save to a directory (which should fail)
        subdir = tmp_working_dir / "subdir"
        subdir.mkdir()
        result = save_conversation([], str(subdir))  # path is a directory
        assert result is False

    def test_cleanup_removes_context_file(self, tmp_working_dir):
        ctx_file = tmp_working_dir / "conversation_context.pkl"
        save_conversation([{"role": "user", "content": "test"}], str(ctx_file))
        assert ctx_file.exists()
        cleanup_context()
        assert not ctx_file.exists()

    def test_load_returns_none_for_missing_file(self, tmp_working_dir):
        result = load_conversation(str(tmp_working_dir / "missing.pkl"))
        assert result is None

    def test_save_load_empty_conversation(self, tmp_working_dir):
        save_file = str(tmp_working_dir / "empty.pkl")
        save_conversation([], save_file)
        loaded = load_conversation(save_file)
        assert loaded == []
