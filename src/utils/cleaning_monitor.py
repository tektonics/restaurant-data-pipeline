import pandas as pd
import logging
from pathlib import Path
from ..config.config import CLEANED_RESTAURANTS_CSV

logger = logging.getLogger(__name__)

def get_cleaning_stats():
    """Get statistics about the cleaning process"""
    try:
        if not Path(CLEANED_RESTAURANTS_CSV).exists():
            return {
                'total_entries': 0,
                'missing_cities': 0,
                'complete_entries': 0
            }
            
        df = pd.read_csv(CLEANED_RESTAURANTS_CSV)
        
        stats = {
            'total_entries': len(df),
            'missing_cities': df['City'].isna().sum(),
            'complete_entries': len(df.dropna(subset=['City', 'State', 'Zip']))
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting cleaning stats: {e}")
        return None

def log_cleaning_progress():
    """Log the current progress of the cleaning process"""
    stats = get_cleaning_stats()
    if stats:
        logger.info(f"""
        Cleaning Progress:
        - Total Entries: {stats['total_entries']}
        - Missing Cities: {stats['missing_cities']}
        - Complete Entries: {stats['complete_entries']}
        """) 