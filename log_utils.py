from pathlib import Path


def get_log_file_path() -> Path:
    """Return the absolute path to the application log file."""

    project_dir = Path(__file__).resolve().parent

    return project_dir / "logs" / "app.log"
