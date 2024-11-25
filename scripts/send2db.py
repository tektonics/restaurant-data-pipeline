import pandas as pd
import sys
from src.database import RestaurantDB
from pathlib import Path

def load_csv_to_database():
    print("Starting database loading process...")
    try:
        enhanced_csv = Path("data/processed/cleaned_restaurants_enhanced.csv")
        print(f"Looking for CSV at: {enhanced_csv.absolute()}")
        
        if not enhanced_csv.exists():
            print(f"ERROR: CSV file not found at: {enhanced_csv.absolute()}")
            return False
            
        print("CSV found. Attempting database connection...")
        db = RestaurantDB()
        try:
            db.connect()
            db.create_tables()            
            final_df = pd.read_csv(enhanced_csv)
            if final_df.empty:
                print("ERROR: CSV file is empty")
                return False
            
            valid_df = final_df.dropna(subset=['Restaurant Name'])
            
            if len(valid_df) < len(final_df):
                print(f"Filtered out {len(final_df) - len(valid_df)} invalid records")
            
            print(f"Found {len(valid_df)} valid records to insert")
            
            valid_df = valid_df.replace(r'^\s*$', None, regex=True)
            valid_df = valid_df.replace('Not available', None)
            
            db.insert_restaurant_data(valid_df)
            print("Data successfully loaded into database")
            return True
        finally:
            db.close()
                
    except Exception as e:
        print(f"ERROR: {str(e)}", file=sys.stderr)
        raise

if __name__ == "__main__":
    load_csv_to_database()
