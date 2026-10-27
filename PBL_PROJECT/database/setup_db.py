"""
Hospital Appointment Booking System (HABS)
Database Setup & Seed Script
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.config import Config
from backend.database import init_db, check_mysql_connection

def main():
    print("=" * 60)
    print("Hospital Appointment Booking System - Database Setup")
    print("=" * 60)
    
    ok, msg = check_mysql_connection()
    if ok:
        print(f"[STATUS] MySQL is available at {Config.DB_HOST}:{Config.DB_PORT}")
        print(f"[STATUS] Target database: '{Config.DB_NAME}'")
    else:
        print(f"[STATUS] MySQL check: {msg}")
        print(f"[STATUS] Defaulting to SQLite database at: {Config.SQLITE_PATH}")
        print("[NOTE] To use MySQL, set DB_PASSWORD in backend/config.py or as environment variable.")

    print("\nInitializing database schema and inserting demo records...")
    init_db()
    print("\n[SUCCESS] Database initialization completed successfully!")
    print("=" * 60)

if __name__ == '__main__':
    main()
