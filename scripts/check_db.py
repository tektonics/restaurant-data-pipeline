from src.database import RestaurantDB
import os
from pathlib import Path
from datetime import datetime

def check_database():
    print("\n=== Restaurant Database Diagnostic Report ===")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    db_path = Path('data/database/restaurants.db')
    print(f"Database Location: {db_path.absolute()}")
    
    if not db_path.exists():
        print("ERROR: Database file not found!")
        return

    db = RestaurantDB()
    try:
        db.connect()
        
        db.cursor.execute('SELECT COUNT(*) FROM restaurants')
        count = db.cursor.fetchone()[0]
        print(f"\nTotal Records: {count}")
        
        if count > 0:
            db.cursor.execute('SELECT * FROM restaurants LIMIT 1')
            columns = [description[0] for description in db.cursor.description]
            row = db.cursor.fetchone()
            
            print("\nSample Record Details:")
            print("-" * 50)
            for col, val in zip(columns, row):
                if val is not None:  # Only show non-null values
                    print(f"{col}: {val}")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_database()
