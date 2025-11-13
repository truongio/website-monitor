import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor, Json
from typing import List, Dict, Optional
from contextlib import contextmanager


class DatabaseClient:
    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is required")

    @contextmanager
    def get_connection(self):
        conn = psycopg2.connect(self.database_url)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def add_subscription(self, user_id: int, chat_id: int, url: str) -> Dict:
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    INSERT INTO subscriptions (user_id, chat_id, url, status)
                    VALUES (%s, %s, %s, 'active')
                    ON CONFLICT (user_id, url)
                    DO UPDATE SET status = 'active', updated_at = NOW()
                    RETURNING *
                    """,
                    (user_id, chat_id, url)
                )
                return dict(cur.fetchone())

    def remove_subscription(self, user_id: int, url: str) -> bool:
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM subscriptions WHERE user_id = %s AND url = %s",
                    (user_id, url)
                )
                return cur.rowcount > 0

    def get_user_subscriptions(self, user_id: int) -> List[Dict]:
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM subscriptions WHERE user_id = %s ORDER BY created_at DESC",
                    (user_id,)
                )
                return [dict(row) for row in cur.fetchall()]

    def get_active_subscriptions(self) -> List[Dict]:
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM subscriptions WHERE status = 'active' ORDER BY url"
                )
                return [dict(row) for row in cur.fetchall()]

    def update_subscription_status(self, user_id: int, url: str, status: str) -> bool:
        if status not in ('active', 'paused'):
            raise ValueError(f"Invalid status: {status}")

        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE subscriptions SET status = %s WHERE user_id = %s AND url = %s",
                    (status, user_id, url)
                )
                return cur.rowcount > 0

    def get_page_state(self, url: str) -> Optional[Dict]:
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM page_states WHERE url = %s",
                    (url,)
                )
                row = cur.fetchone()
                return dict(row) if row else None

    def update_page_state(self, url: str, content_hash: str, last_content: Optional[str] = None) -> Dict:
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    INSERT INTO page_states (url, content_hash, last_content, last_checked)
                    VALUES (%s, %s, %s, NOW())
                    ON CONFLICT (url)
                    DO UPDATE SET
                        content_hash = EXCLUDED.content_hash,
                        last_content = EXCLUDED.last_content,
                        last_checked = NOW()
                    RETURNING *
                    """,
                    (url, content_hash, last_content)
                )
                return dict(cur.fetchone())

    def get_subscriptions_for_url(self, url: str) -> List[Dict]:
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM subscriptions WHERE url = %s AND status = 'active'",
                    (url,)
                )
                return [dict(row) for row in cur.fetchall()]

    def update_forum_thread_state(self, url: str, last_post_number: int,
                                   last_post_id: Optional[str] = None,
                                   metadata: Optional[Dict] = None) -> Dict:
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    INSERT INTO page_states (url, monitoring_type, last_post_number, last_post_id, metadata, last_checked)
                    VALUES (%s, 'forum_thread', %s, %s, %s, NOW())
                    ON CONFLICT (url)
                    DO UPDATE SET
                        monitoring_type = 'forum_thread',
                        last_post_number = EXCLUDED.last_post_number,
                        last_post_id = EXCLUDED.last_post_id,
                        metadata = EXCLUDED.metadata,
                        last_checked = NOW()
                    RETURNING *
                    """,
                    (url, last_post_number, last_post_id, Json(metadata) if metadata else None)
                )
                return dict(cur.fetchone())
