import psycopg2
import os
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()
def test_supabase_connection():
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    try:
        print(f"📡 Testing connection to: {database_url}")
        
        # Parse the URL
        parsed = urlparse(database_url)
        
        # Extract connection parameters
        connection_params = {
            'host': parsed.hostname,
            'port': parsed.port or 5432,
            'database': parsed.path[1:],  # Remove leading '/'
            'user': parsed.username,
            'password': parsed.password
        }
        
        print(f"📍 Host: {connection_params['host']}")
        print(f"🔌 Port: {connection_params['port']}")
        print(f"📚 Database: {connection_params['database']}")
        
        # Test connection
        conn = psycopg2.connect(**connection_params)
        cursor = conn.cursor()
        
        # Execute a simple query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Connected successfully!")
        print(f"🐘 PostgreSQL Version: {version[0]}")
        
        # Test a simple table query
        cursor.execute("SELECT COUNT(*) FROM tenants;")
        count = cursor.fetchone()
        print(f"📊 Tenants table count: {count[0]}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_supabase_connection()