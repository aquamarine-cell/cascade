"""Tests for plugin system."""

import pytest
import tempfile
from pathlib import Path
from cascade.plugins import FileOpsPlugin


def test_file_write_and_read():
    """Test writing and reading files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "test.txt"
        content = "Hello, Cascade!"
        
        FileOpsPlugin.write_file(str(file_path), content)
        read_content = FileOpsPlugin.read_file(str(file_path))
        
        assert read_content == content


def test_file_append():
    """Test appending to files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "append.txt"
        
        FileOpsPlugin.write_file(str(file_path), "Line 1\n")
        FileOpsPlugin.append_file(str(file_path), "Line 2\n")
        
        content = FileOpsPlugin.read_file(str(file_path))
        assert content == "Line 1\nLine 2\n"


def test_list_files():
    """Test listing directory contents."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create some files
        Path(tmpdir, "file1.txt").write_text("content1")
        Path(tmpdir, "file2.txt").write_text("content2")
        
        files = FileOpsPlugin.list_files(tmpdir)
        
        assert len(files) >= 2
        assert any("file1" in f for f in files)
        assert any("file2" in f for f in files)


def test_read_nonexistent_file():
    """Test reading nonexistent file returns error."""
    result = FileOpsPlugin.read_file("/nonexistent/path/file.txt")
    assert "Error" in result
