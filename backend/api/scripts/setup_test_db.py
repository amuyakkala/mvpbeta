import sqlite3
import sys
from pathlib import Path
from datetime import datetime
import json

def setup_test_database(db_path: str) -> bool:
    """
    Setup test database with sample data.
    
    Args:
        db_path: Path to database file
        
    Returns:
        bool indicating if setup was successful
    """
    try:
        # Create database directory if it doesn't exist
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                email TEXT UNIQUE,
                password_hash TEXT,
                role TEXT,
                created_at TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS traces (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                trace_data JSON,
                created_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS issues (
                id INTEGER PRIMARY KEY,
                trace_id INTEGER,
                title TEXT,
                description TEXT,
                severity TEXT,
                status TEXT,
                assigned_to_user_id INTEGER,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                FOREIGN KEY (trace_id) REFERENCES traces (id),
                FOREIGN KEY (assigned_to_user_id) REFERENCES users (id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                action_type TEXT,
                metadata JSON,
                created_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Insert test user
        cursor.execute("""
            INSERT INTO users (email, password_hash, role, created_at)
            VALUES (?, ?, ?, ?)
        """, (
            "admin@test.com",
            "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # password123
            "admin",
            datetime.now().isoformat()
        ))
        
        # Insert test trace
        test_trace = {
            "timestamp": datetime.now().isoformat(),
            "level": "INFO",
            "message": "Test trace message",
            "metadata": {
                "service": "test-service",
                "version": "1.0.0"
            }
        }
        
        cursor.execute("""
            INSERT INTO traces (user_id, trace_data, created_at)
            VALUES (?, ?, ?)
        """, (
            1,
            json.dumps(test_trace),
            datetime.now().isoformat()
        ))
        
        # Insert test issue
        cursor.execute("""
            INSERT INTO issues (
                trace_id, title, description, severity, status,
                assigned_to_user_id, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            1,
            "Test Issue",
            "This is a test issue",
            "medium",
            "open",
            1,
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        
        # Insert test audit log
        cursor.execute("""
            INSERT INTO audit_logs (user_id, action_type, metadata, created_at)
            VALUES (?, ?, ?, ?)
        """, (
            1,
            "test_action",
            json.dumps({"test": "data"}),
            datetime.now().isoformat()
        ))
        
        conn.commit()
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
        print("Usage: python setup_test_db.py <database_path>")
        sys.exit(1)
    
    db_path = sys.argv[1]
    if setup_test_database(db_path):
        print("Test database setup successful")
        sys.exit(0)
    else:
        print("Test database setup failed")
        sys.exit(1) 