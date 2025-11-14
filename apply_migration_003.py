from dotenv import load_dotenv
from database import DatabaseClient

load_dotenv()

db = DatabaseClient()

print("Applying migration 003 (selectors support)...")

migration_sql = """
-- Add selectors column to page_states table (JSON array of CSS selectors)
ALTER TABLE page_states
ADD COLUMN IF NOT EXISTS selectors JSONB DEFAULT NULL;

-- Add selectors column to subscriptions table
ALTER TABLE subscriptions
ADD COLUMN IF NOT EXISTS selectors JSONB DEFAULT NULL;

-- Add comment to explain the feature
COMMENT ON COLUMN page_states.selectors IS 'JSON array of CSS selectors to monitor specific elements instead of entire page';
COMMENT ON COLUMN subscriptions.selectors IS 'JSON array of CSS selectors to monitor specific elements instead of entire page';
"""

with db.get_connection() as conn:
    with conn.cursor() as cur:
        cur.execute(migration_sql)
        print("✅ Migration applied successfully!")

print("\nYou can now use /watch command with CSS selectors!")
