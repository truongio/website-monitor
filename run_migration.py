from dotenv import load_dotenv
from database import DatabaseClient

load_dotenv()

db = DatabaseClient()

print("Running database migration 002...")

with open('database/migration_002_forum_support.sql', 'r') as f:
    migration_sql = f.read()

with db.get_connection() as conn:
    with conn.cursor() as cur:
        cur.execute(migration_sql)

print("Migration completed successfully!")
