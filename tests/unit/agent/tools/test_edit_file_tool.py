"""Unit tests for agent/tools/edit_file_tool.py"""
import pytest

from tools.edit_file_tool import edit_file


class TestEditFileTool:
    def test_creates_new_file_when_old_str_empty(self, tmp_working_dir):
        result = edit_file({"path": "new_file.txt", "old_str": "", "new_str": "hello world"})
        assert "created" in result.lower()
        assert (tmp_working_dir / "new_file.txt").read_text() == "hello world"

    def test_overwrites_content_via_replace(self, tmp_working_dir):
        f = tmp_working_dir / "existing.txt"
        f.write_text("old content here")
        result = edit_file({"path": "existing.txt", "old_str": "old content", "new_str": "new content"})
        assert result == "OK"
        assert "new content" in f.read_text()

    def test_returns_success_message_on_create(self, tmp_working_dir):
        result = edit_file({"path": "created.txt", "old_str": "", "new_str": "data"})
        assert "created.txt" in result

    def test_raises_error_when_old_str_not_found(self, tmp_working_dir):
        (tmp_working_dir / "file.txt").write_text("some content")
        with pytest.raises(ValueError, match="not found"):
            edit_file({"path": "file.txt", "old_str": "missing text", "new_str": "replacement"})

    def test_creates_parent_directories(self, tmp_working_dir):
        result = edit_file({
            "path": "subdir/nested/file.txt",
            "old_str": "",
            "new_str": "nested content",
        })
        assert "created" in result.lower()
        assert (tmp_working_dir / "subdir" / "nested" / "file.txt").exists()

    def test_raises_when_old_str_equals_new_str(self, tmp_working_dir):
        (tmp_working_dir / "file.txt").write_text("content")
        with pytest.raises(ValueError):
            edit_file({"path": "file.txt", "old_str": "same", "new_str": "same"})

    def test_raises_when_new_str_empty(self, tmp_working_dir):
        (tmp_working_dir / "file.txt").write_text("content")
        with pytest.raises(ValueError):
            edit_file({"path": "file.txt", "old_str": "content", "new_str": ""})

    def test_raises_file_not_found_when_file_missing_and_old_str_nonempty(self, tmp_working_dir):
        with pytest.raises(FileNotFoundError):
            edit_file({"path": "missing.txt", "old_str": "something", "new_str": "other"})
