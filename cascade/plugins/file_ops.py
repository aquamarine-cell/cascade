"""File operations plugin for Cascade."""

from pathlib import Path
from typing import Optional


class FileOpsPlugin:
    """Handle file reading and writing operations."""

    @staticmethod
    def read_file(path: str) -> Optional[str]:
        """Read file contents."""
        try:
            with open(Path(path).expanduser(), "r") as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {e}"

    @staticmethod
    def write_file(path: str, content: str) -> bool:
        """Write content to file."""
        try:
            file_path = Path(path).expanduser()
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w") as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error writing file: {e}")
            return False

    @staticmethod
    def list_files(path: str = ".") -> list[str]:
        """List files in a directory."""
        try:
            return [str(f) for f in Path(path).expanduser().iterdir()]
        except Exception as e:
            return [f"Error: {e}"]

    @staticmethod
    def append_file(path: str, content: str) -> bool:
        """Append content to file."""
        try:
            with open(Path(path).expanduser(), "a") as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error appending to file: {e}")
            return False
