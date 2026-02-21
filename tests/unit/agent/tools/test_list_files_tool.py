"""Unit tests for agent/tools/list_files_tool.py"""
import json

import pytest

from tools.list_files_tool import list_files


class TestListFilesTool:
    def test_lists_files_in_populated_directory(self, tmp_working_dir):
        (tmp_working_dir / "file1.txt").write_text("a")
        (tmp_working_dir / "file2.py").write_text("b")
        result = json.loads(list_files({"path": "."}))
        assert any("file1.txt" in entry for entry in result)
        assert any("file2.py" in entry for entry in result)

    def test_returns_empty_for_empty_directory(self, tmp_working_dir):
        empty_dir = tmp_working_dir / "empty"
        empty_dir.mkdir()
        result = json.loads(list_files({"path": "empty"}))
        assert result == []

    def test_raises_file_not_found_for_nonexistent_path(self, tmp_working_dir):
        with pytest.raises(FileNotFoundError):
            list_files({"path": "nonexistent_dir"})

    def test_raises_not_a_directory_error_for_file(self, tmp_working_dir):
        (tmp_working_dir / "afile.txt").write_text("data")
        with pytest.raises(NotADirectoryError):
            list_files({"path": "afile.txt"})

    def test_directories_have_trailing_slash(self, tmp_working_dir):
        subdir = tmp_working_dir / "subdir"
        subdir.mkdir()
        result = json.loads(list_files({"path": "."}))
        # At least one entry should end with "/"
        assert any(entry.endswith("/") for entry in result)

    def test_excludes_pycache(self, tmp_working_dir):
        pycache = tmp_working_dir / "__pycache__"
        pycache.mkdir()
        (pycache / "module.pyc").write_bytes(b"")
        result = json.loads(list_files({"path": "."}))
        assert not any("__pycache__" in entry for entry in result)

    def test_excludes_git_directory(self, tmp_working_dir):
        git_dir = tmp_working_dir / ".git"
        git_dir.mkdir()
        (git_dir / "config").write_text("config")
        result = json.loads(list_files({"path": "."}))
        assert not any(".git" in entry for entry in result)

    def test_returns_json_string(self, tmp_working_dir):
        (tmp_working_dir / "f.txt").write_text("x")
        result = list_files({"path": "."})
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert isinstance(parsed, list)
