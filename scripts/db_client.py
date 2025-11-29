import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_db_connection():
    """
    Establishes a connection to the database using DATABASE_URL from .env.
    Returns a psycopg2 connection object or None if connection fails.
    """
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("Error: DATABASE_URL is not set in .env")
        print("Please add DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres to your .env file.")
        return None

    try:
        conn = psycopg2.connect(database_url)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None
