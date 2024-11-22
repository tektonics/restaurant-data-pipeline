import pandas as pd
import sys
from src.database import RestaurantDB
from pathlib import Path

def load_csv_to_database():
    print("Starting database loading process...")  # Basic print statement
    
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
                
            print(f"Found {len(final_df)} records to insert")
            db.insert_restaurant_data(final_df)
            print("Data successfully loaded into database")
            return True
        finally:
            db.close()
                
    except Exception as e:
        print(f"ERROR: {str(e)}", file=sys.stderr)
        raise

if __name__ == "__main__":
    print("Script is starting...")  # Verify script is running
    try:
        success = load_csv_to_database()
        if not success:
            print("Database loading process failed or was skipped")
    except Exception as e:
        print(f"Fatal error: {str(e)}", file=sys.stderr)
        sys.exit(1)
    print("Script completed")
