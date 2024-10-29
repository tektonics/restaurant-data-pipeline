from src.database import RestaurantDB
import os
from pathlib import Path
from datetime import datetime

def check_database():
    print("\n=== Restaurant Database Diagnostic Report ===")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Verify database file
    db_path = Path('data/database/restaurants.db')
    print("[1/3] Database File Verification")
    print(f"Target Location: {db_path.absolute()}")
    
    if not db_path.exists():
        print("Status: Database file not found")
        print("\nRecommended Actions:")
        print("• Initialize the database by running main.py")
        print("• Verify database path configuration")
        return

    print(f"Status: Located successfully ({os.path.getsize(db_path) / 1024:.2f} KB)")

    # Database connection and schema verification
    db = RestaurantDB()
    try:
        print("\n[2/3] Connection Test")
        db.connect()
        print("Status: Connection established successfully")
        
        # Verify table structure
        print("\n[3/3] Schema Verification")
        db.cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='restaurants'
        """)
        if not db.cursor.fetchone():
            print("Status: Schema validation failed - 'restaurants' table not found")
            return
            
        # Data analysis
        db.cursor.execute('SELECT COUNT(*) FROM restaurants')
        count = db.cursor.fetchone()[0]
        print("\n=== Data Analysis ===")
        print(f"Total Records: {count:,}")
        
        if count > 0:
            db.cursor.execute('''
                SELECT restaurant_name, city, state 
                FROM restaurants 
                LIMIT 5
            ''')
            print("\nSample Records:")
            for row in db.cursor.fetchall():
                print(f"\nEstablishment: {row[0]}")
                print(f"Location: {row[1]}, {row[2]}")
                print("-" * 50)
        else:
            print("\nNotice: Database contains no records")
            print("\nRecommended Actions:")
            print("• Execute data import process via main.py")
            print("• Review data pipeline logs for potential issues")
    
    except Exception as e:
        print(f"\nError Report:")
        print(f"An error occurred during database inspection: {e}")
    finally:
        db.close()
        print("\n=== End of Database Diagnostic Report ===")

if __name__ == "__main__":
    check_database()
