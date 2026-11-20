from pathlib import Path

from log_utils import get_log_file_path


def test_get_log_file_path():
    """Verify the utility returns the expected log file path."""

    result = get_log_file_path()

    assert isinstance(result, Path)
    assert result.is_absolute()
    assert result.name == "app.log"
    assert result.parent.name == "logs"
