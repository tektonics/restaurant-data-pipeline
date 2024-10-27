"""Database configuration settings"""

import os
from pathlib import Path

# Base project directory
PROJECT_ROOT = Path("S:/restaurant_data_project")

# Database settings
DATABASE = {
    'path': PROJECT_ROOT / 'data' / 'database' / 'restaurants.db',
    'backup_path': PROJECT_ROOT / 'data' / 'database' / 'backups',
    'log_path': PROJECT_ROOT / 'logs' / 'database.log'
}

# Table schemas
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
        'instagram_name',
        'instagram_url'
    ]
}

# Create necessary directories
for path in [DATABASE['path'].parent, DATABASE['backup_path'], DATABASE['log_path'].parent]:
    path.mkdir(parents=True, exist_ok=True)