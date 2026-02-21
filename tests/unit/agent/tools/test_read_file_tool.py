"""Unit tests for agent/tools/read_file_tool.py"""
import pytest

from tools.read_file_tool import read_file


class TestReadFileTool:
    def test_reads_existing_file(self, tmp_working_dir):
        f = tmp_working_dir / "hello.txt"
        f.write_text("hello world")
        result = read_file({"path": "hello.txt"})
        assert result == "hello world"

    def test_reads_multiline_file(self, tmp_working_dir):
        content = "line1\nline2\nline3\n"
        (tmp_working_dir / "multi.txt").write_text(content)
        result = read_file({"path": "multi.txt"})
        assert result == content

    def test_raises_file_not_found_for_missing_file(self, tmp_working_dir):
        with pytest.raises(FileNotFoundError):
            read_file({"path": "nonexistent.txt"})

    def test_raises_is_a_directory_error_for_directory(self, tmp_working_dir):
        subdir = tmp_working_dir / "mydir"
        subdir.mkdir()
        with pytest.raises(IsADirectoryError):
            read_file({"path": "mydir"})

    def test_accepts_json_string_input(self, tmp_working_dir):
        import json
        (tmp_working_dir / "file.txt").write_text("content")
        result = read_file(json.dumps({"path": "file.txt"}))
        assert result == "content"

    def test_reads_specific_line_range(self, tmp_working_dir):
        lines = "\n".join(f"line{i}" for i in range(1, 6))
        (tmp_working_dir / "lines.txt").write_text(lines)
        result = read_file({"path": "lines.txt", "start_line": 2, "end_line": 3})
        assert "line2" in result
        assert "line3" in result
        assert "line1" not in result
        assert "line4" not in result

    def test_path_traversal_nonexistent_raises(self, tmp_working_dir):
        with pytest.raises(FileNotFoundError):
            read_file({"path": "../../nonexistent_file_xyz.txt"})
