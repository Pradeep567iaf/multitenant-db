import psycopg2
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Fetch variables from the transaction pooler format
USER = os.getenv("PG_USER") or "postgres.rcogovxnlzmhgbyfnjfp"
PASSWORD = os.getenv("PG_PASSWORD") or "bFqYfNvdaxIC36SA"
HOST = os.getenv("PG_HOST") or "aws-1-ap-northeast-2.pooler.supabase.com"
PORT = os.getenv("PG_PORT") or "6543"
DBNAME = os.getenv("PG_DBNAME") or "postgres"

print(f"Testing Transaction Pooler Connection:")
print(f"User: {USER}")
print(f"Host: {HOST}")
print(f"Port: {PORT}")
print(f"Database: {DBNAME}")
print("-" * 50)

# Connect to the database
try:
    connection = psycopg2.connect(
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT,
        dbname=DBNAME
    )
    print("✅ Connection successful!")
    
    # Create a cursor to execute SQL queries
    cursor = connection.cursor()
    
    # Test queries
    cursor.execute("SELECT NOW();")
    result = cursor.fetchone()
    print(f"⏱️  Current Time: {result[0]}")
    
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"🐘 PostgreSQL Version: {version[0][:50]}...")
    
    cursor.execute("SELECT COUNT(*) FROM tenants;")
    count = cursor.fetchone()
    print(f"📊 Tenants table count: {count[0]}")
    
    # Close the cursor and connection
    cursor.close()
    connection.close()
    print("🔒 Connection closed.")
    
except Exception as e:
    print(f"❌ Failed to connect: {e}")