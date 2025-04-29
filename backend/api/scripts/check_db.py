import sqlite3
import sys
from pathlib import Path

def check_database(db_path: str) -> bool:
    """
    Check database health and connectivity.
    
    Args:
        db_path: Path to database file
        
    Returns:
        bool indicating if database is healthy
    """
    try:
        # Check if database file exists
        if not Path(db_path).exists():
            print(f"Database file not found at {db_path}")
            return False
        
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        required_tables = {'users', 'traces', 'issues', 'audit_logs'}
        existing_tables = {table[0] for table in tables}
        
        missing_tables = required_tables - existing_tables
        if missing_tables:
            print(f"Missing required tables: {missing_tables}")
            return False
        
        # Check table schemas
        for table in required_tables:
            cursor.execute(f"PRAGMA table_info({table});")
            columns = cursor.fetchall()
            if not columns:
                print(f"Table {table} has no columns")
                return False
        
        # Check sample data
        cursor.execute("SELECT COUNT(*) FROM users;")
        user_count = cursor.fetchone()[0]
        if user_count == 0:
            print("No users found in database")
            return False
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python check_db.py <database_path>")
        sys.exit(1)
    
    db_path = sys.argv[1]
    if check_database(db_path):
        print("Database is healthy")
        sys.exit(0)
    else:
        print("Database check failed")
        sys.exit(1) 