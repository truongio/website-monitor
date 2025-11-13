from dotenv import load_dotenv
from database import DatabaseClient

load_dotenv()

db = DatabaseClient()

# Force a change by updating the stored hash to something different
print("Forcing a change detection for next monitor run...")
db.update_page_state(
    url='https://news.ycombinator.com',
    content_hash='test_old_hash_to_force_change',
    last_content='This will trigger a change notification'
)
print("Done! Run the monitor script now and you'll get a notification.")
