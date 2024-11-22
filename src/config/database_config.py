import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent

DATABASE = {
    'path': PROJECT_ROOT / 'data' / 'database' / 'restaurants.db',
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

for path in [DATABASE['path'].parent, DATABASE['backup_path'], DATABASE['log_path'].parent]:
    path.mkdir(parents=True, exist_ok=True)
