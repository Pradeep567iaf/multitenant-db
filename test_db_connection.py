#!/usr/bin/env python3
"""
Test PostgreSQL connection
"""

import psycopg2
import sys
from urllib.parse import urlparse

def test_connection(database_url):
    """Test database connection"""
    try:
        print(f"Connecting to: {database_url}")
        
        # Parse URL
        parsed = urlparse(database_url)
        
        # Connect
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            database=parsed.path[1:],  # Remove leading '/'
            user=parsed.username,
            password=parsed.password
        )
        
        # Test query
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()
        print(f"✅ Connected successfully!")
        print(f"PostgreSQL Version: {version[0]}")
        
        # Test simple query
        cur.execute("SELECT current_database(), current_user;")
        db, user = cur.fetchone()
        print(f"Database: {db}")
        print(f"User: {user}")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    # Get database URL from command line or environment
    if len(sys.argv) > 1:
        db_url = sys.argv[1]
    else:
        db_url = input("Enter DATABASE_URL: ")
    
    if test_connection(db_url):
        print("\n🎉 Connection test PASSED!")
        sys.exit(0)
    else:
        print("\n💥 Connection test FAILED!")
        sys.exit(1)
