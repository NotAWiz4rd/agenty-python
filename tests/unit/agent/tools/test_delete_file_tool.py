"""Unit tests for agent/tools/delete_file_tool.py"""
import pytest

from tools.delete_file_tool import delete_file


class TestDeleteFileTool:
    def test_deletes_existing_file(self, tmp_working_dir):
        f = tmp_working_dir / "to_delete.txt"
        f.write_text("content")
        result = delete_file({"path": "to_delete.txt"})
        assert not f.exists()
        assert "Successfully deleted" in result

    def test_returns_success_message(self, tmp_working_dir):
        f = tmp_working_dir / "file.txt"
        f.write_text("data")
        result = delete_file({"path": "file.txt"})
        assert "file.txt" in result

    def test_raises_file_not_found_for_missing_file(self, tmp_working_dir):
        with pytest.raises(FileNotFoundError):
            delete_file({"path": "nonexistent.txt"})

    def test_raises_is_a_directory_error_for_directory(self, tmp_working_dir):
        subdir = tmp_working_dir / "mydir"
        subdir.mkdir()
        with pytest.raises(IsADirectoryError):
            delete_file({"path": "mydir"})

    def test_raises_value_error_for_empty_path(self, tmp_working_dir):
        with pytest.raises(ValueError):
            delete_file({"path": ""})

    def test_accepts_json_string_input(self, tmp_working_dir):
        import json
        f = tmp_working_dir / "file.txt"
        f.write_text("data")
        result = delete_file(json.dumps({"path": "file.txt"}))
        assert not f.exists()
        assert "Successfully deleted" in result
