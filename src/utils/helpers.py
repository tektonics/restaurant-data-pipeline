from pathlib import Path

def ensure_directories_exist(file_path: Path) -> None:
    """Ensure all parent directories exist for a given file path"""
    file_path.parent.mkdir(parents=True, exist_ok=True)

def get_project_root() -> Path:
    """Returns project root directory"""
    return Path(__file__).parent.parent.parent

