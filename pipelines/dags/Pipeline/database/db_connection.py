import psycopg2
from config.config import  *    # Import all config variables

def get_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
            connect_timeout=5  # Add timeout to prevent hanging
        )
        return conn
    except Exception as e:
        print(f"Warning: Database connection failed: {e}")
        return None