from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def ensure_project_directories():
    """Ensure all required project directories exist"""
    directories = [
        'data/raw',
        'data/processed',
        'data/database',
        'data/database/backups',
        'logs'
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ensured directory exists: {dir_path}")

def get_project_root():
    """Returns project root directory"""
    return Path(__file__).parent.parent.parent 