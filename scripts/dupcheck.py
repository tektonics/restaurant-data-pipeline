import pandas as pd
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def find_missing_restaurants():
    try:
        # Define paths
        cleaned_path = Path("data/raw/cleaned_restaurants.csv")
        cleaned_enhanced_path = Path("data/processed/cleaned_restaurants_enhanced.csv")
        output_path = Path("data/raw/missing_restaurants.csv")
        
        # Create output directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Read the CSV files
        logger.info("Reading CSV files...")
        cleaned_df = pd.read_csv(cleaned_path)
        cleaned_enhanced_df = pd.read_csv(cleaned_enhanced_path) if cleaned_enhanced_path.exists() else pd.DataFrame()
        
        # Get sets of restaurant names from each file
        cleaned_names = set(cleaned_df['Restaurant Name'])
        cleaned_enhanced_names = set(cleaned_enhanced_df['Restaurant Name']) if not cleaned_enhanced_df.empty else set()
        
        # Find restaurants that are in cleaned but not in enhanced file
        missing_names = cleaned_names - cleaned_enhanced_names
        
        # Get the full records for missing restaurants
        missing_df = cleaned_df[cleaned_df['Restaurant Name'].isin(missing_names)]
        
        # Save missing restaurants to CSV
        missing_df.to_csv(output_path, index=False)
        logger.info(f"Found {len(missing_df)} missing restaurants. Saved to {output_path}")
        
        return len(missing_df)
        
    except Exception as e:
        logger.error(f"Error finding missing restaurants: {e}")
        raise

if __name__ == "__main__":
    find_missing_restaurants()