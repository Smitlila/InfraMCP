import server
import pytest


def test_read_logs_returns_recent_entries(tmp_path, monkeypatch):
    # Create a temporary log file
    test_file = tmp_path / "test.log"

    test_file.write_text(
        "INFO First entry\n"
        "INFO Second entry\n"
        "ERROR Third entry\n"
        "INFO Fourth entry\n"
        "INFO Fifth entry\n",
        encoding="utf-8"
    )

    # Replace the real log path with our test file
    monkeypatch.setattr(
        server,
        "get_log_file_path",
        lambda: test_file
    )

    # Execute the underlying Python function
    result = server.read_logs(lines=2)

    # Verify the result
    assert result["status"] == "success"
    assert result["requested_lines"] == 2
    assert result["returned_lines"] == 2
    assert result["logs"] == [
        "INFO Fourth entry",
        "INFO Fifth entry"
    ]


def test_search_logs_finds_keyword(tmp_path, monkeypatch):
    """Verify that log searching is case-insensitive."""

    # Create a temporary log file
    test_file = tmp_path / "test.log"

    test_file.write_text(
        "INFO Server started\n"
        "ERROR Database connection failed\n"
        "WARN High memory usage\n"
        "INFO DATABASE connection restored\n"
        "ERROR Payment timeout\n",
        encoding="utf-8"
    )

    # Replace the real log path with our temporary file
    monkeypatch.setattr(
        server,
        "get_log_file_path",
        lambda: test_file
    )

    # Execute the search tool
    result = server.search_logs(keyword="database")

    # Verify the results
    assert result["status"] == "success"
    assert result["keyword"] == "database"
    assert result["total_matches"] == 2

    assert result["logs"] == [
        "ERROR Database connection failed",
        "INFO DATABASE connection restored"
    ]


def test_count_errors(tmp_path, monkeypatch):
    """Verify error counting and malformed log detection."""

    # Create a temporary log file
    test_file = tmp_path / "test.log"

    test_file.write_text(
        "2026-11-18 10:00:01 INFO Server started\n"
        "2026-11-18 10:01:00 ERROR Database connection failed\n"
        "2026-11-18 10:02:00 WARN High memory usage\n"
        "2026-11-18 10:03:00 CRITICAL Worker crashed\n"
        "2026-11-18 10:04:00 ERROR Payment timeout\n"
        "INVALID LOG ENTRY\n",
        encoding="utf-8"
    )

    # Replace the real log file path
    monkeypatch.setattr(
        server,
        "get_log_file_path",
        lambda: test_file
    )

    # Execute the function
    result = server.count_errors()

    # Verify the returned values
    assert result["status"] == "success"
    assert result["total_logs"] == 5
    assert result["error_count"] == 2
    assert result["critical_count"] == 1
    assert result["total_error_events"] == 3
    assert result["invalid_logs"] == 1


def test_read_logs_missing_file(tmp_path, monkeypatch):
    """Verify read_logs handles a missing log file."""

    # Point to a file that does not exist
    missing_file = tmp_path / "missing.log"

    # Replace the real log path with the missing file
    monkeypatch.setattr(
        server,
        "get_log_file_path",
        lambda: missing_file
    )

    # Execute the tool
    result = server.read_logs(lines=5)

    # Verify the error response
    assert result["status"] == "error"
    assert result["message"] == "Application log file not found"


@pytest.mark.parametrize("lines", [0, -5, 101])
def test_read_logs_invalid_lines(lines):
    """Verify read_logs rejects invalid line counts."""

    result = server.read_logs(lines=lines)

    assert result["status"] == "error"
    assert result["message"] == "lines must be between 1 and 100"


@pytest.mark.parametrize("keyword", ["", "   ", "\t"])
def test_search_logs_empty_keyword(keyword):
    """Verify search_logs rejects empty or whitespace-only keywords."""

    result = server.search_logs(keyword=keyword)

    assert result["status"] == "error"
    assert result["message"] == "Search keyword cannot be empty"



def test_search_logs_missing_file(tmp_path, monkeypatch):
    """Verify search_logs handles a missing log file."""

    # Create a path to a file that does not exist
    missing_file = tmp_path / "missing.log"

    # Redirect the log path to our nonexistent file
    monkeypatch.setattr(
        server,
        "get_log_file_path",
        lambda: missing_file
    )

    # Execute the search tool
    result = server.search_logs(keyword="database")

    # Verify the error response
    assert result["status"] == "error"
    assert result["message"] == "Application log file not found"


def test_count_errors_missing_file(tmp_path, monkeypatch):
    """Verify count_errors handles a missing log file."""

    # Create a path without creating the actual file
    missing_file = tmp_path / "missing.log"

    # Confirm the file does not exist
    assert not missing_file.exists()

    # Redirect the log path to the missing file
    monkeypatch.setattr(
        server,
        "get_log_file_path",
        lambda: missing_file
    )

    # Execute the function
    result = server.count_errors()

    # Verify the error response
    assert result["status"] == "error"
    assert result["message"] == "Application log file not found"


def test_read_logs_invalid_utf8(tmp_path, monkeypatch):
    """Verify read_logs handles invalid UTF-8 data."""

    # Create a temporary log file
    test_file = tmp_path / "invalid.log"

    # Write invalid UTF-8 bytes
    test_file.write_bytes(b"\xff")

    # Redirect the log path to our test file
    monkeypatch.setattr(
        server,
        "get_log_file_path",
        lambda: test_file
    )

    # Execute the function
    result = server.read_logs(lines=5)

    # Verify the error response
    assert result["status"] == "error"
    assert result["message"] == ("Log file contains non-text data or is not UTF-8 encoded")


def test_search_logs_invalid_utf8(tmp_path, monkeypatch):
    """Verify search_logs handles invalid UTF-8 data."""

    # Create a temporary log file
    test_file = tmp_path / "invalid.log"

    # Write invalid UTF-8 bytes
    test_file.write_bytes(b"\xff")

    # Redirect the log path to the temporary file
    monkeypatch.setattr(
        server,
        "get_log_file_path",
        lambda: test_file
    )

    # Execute the search tool
    result = server.search_logs(keyword="database")

    # Verify the error response
    assert result["status"] == "error"
    assert "UTF-8" in result["message"]


def test_count_errors_invalid_utf8(tmp_path, monkeypatch):
    """Verify count_errors handles invalid UTF-8 data."""

    # Create a temporary log file
    test_file = tmp_path / "invalid.log"

    # Write invalid UTF-8 bytes
    test_file.write_bytes(b"\xff")

    # Redirect count_errors to our temporary file
    monkeypatch.setattr(
        server,
        "get_log_file_path",
        lambda: test_file
    )

    # Execute the function
    result = server.count_errors()

    # Verify the error response
    assert result["status"] == "error"
    assert "UTF-8" in result["message"]
