import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent

DATABASE = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'restaurants_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', ''),
    'backup_path': PROJECT_ROOT / 'data' / 'database' / 'backups',
    'log_path': PROJECT_ROOT / 'logs' / 'database.log'
}

RESTAURANT_SCHEMA = {
    'core_fields': [
        'restaurant_name',
        'restaurant_description',
        'cleaned_address',
        'city',
        'state',
        'zip',
        'phone',
        'website',
        'google_maps_link',
    ]
}

DATABASE['backup_path'].mkdir(parents=True, exist_ok=True)
