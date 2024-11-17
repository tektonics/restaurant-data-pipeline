import csv
from pathlib import Path
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def ensure_csv_exists(filepath, fieldnames):
    """Ensure CSV file exists with headers"""
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    if not filepath.exists():
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

def write_row(filepath, row_data, fieldnames):
    """Write a single row to CSV file"""
    with open(filepath, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writerow(row_data)

def is_duplicate(filepath, key_fields, row_data):
    """Check if row already exists based on key fields"""
    if not Path(filepath).exists():
        return False
        
    try:
        df = pd.read_csv(filepath)
        for _, row in df.iterrows():
            if all(row[field] == row_data[field] for field in key_fields):
                return True
        return False
    except Exception as e:
        logger.error(f"Error checking duplicates: {e}")
        return False
