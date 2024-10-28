from pathlib import Path

def get_project_root():
    """Returns the project root directory"""
    return Path(__file__).parent.parent.parent

def get_config_path():
    """Returns the config directory path"""
    return get_project_root() / "config"

