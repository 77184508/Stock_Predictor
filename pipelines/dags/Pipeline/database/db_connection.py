import os
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from config.config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD


def ensure_db_config():
    missing = [name for name, value in {
        "DB_HOST": DB_HOST,
        "DB_PORT": DB_PORT,
        "DB_NAME": DB_NAME,
        "DB_USER": DB_USER,
        "DB_PASSWORD": DB_PASSWORD,
    }.items() if not value]
    if missing:
        raise ValueError(f"Missing required DB config(s): {', '.join(missing)}")


def ensure_database_exists():
    ensure_db_config()
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database="postgres",
            user=DB_USER,
            password=DB_PASSWORD,
            port=int(DB_PORT),
            connect_timeout=5
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
        exists = cur.fetchone() is not None
        if not exists:
            cur.execute(sql.SQL("CREATE DATABASE {};").format(sql.Identifier(DB_NAME)))
        cur.close()
        conn.close()
    except Exception as e:
        raise ConnectionError(f"Unable to ensure database exists '{DB_NAME}': {e}")


def create_tables():
    schema_file = os.path.join(os.path.dirname(__file__), "schema.sql")
    if not os.path.isfile(schema_file):
        raise FileNotFoundError(f"Schema file not found: {schema_file}")

    with open(schema_file, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    conn = get_connection(do_schema=False)
    if conn is None:
        raise ConnectionError("Failed to create tables because DB connection could not be established")

    try:
        cur = conn.cursor()
        cur.execute(schema_sql)
        conn.commit()
        cur.close()
    finally:
        conn.close()


def get_connection(do_schema=True):
    if not all([DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD]):
        raise ValueError("Database connection parameters are not fully set")

    if do_schema:
        ensure_database_exists()

    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
            connect_timeout=5
        )

        if do_schema:
            create_tables()

        return conn
    except Exception as e:
        raise ConnectionError(f"Database connection failed: {e}")
