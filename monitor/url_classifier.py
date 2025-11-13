import re
from typing import Tuple, Dict, Optional
from urllib.parse import urlparse


class URLClassifier:
    FORUM_PATTERNS = [
        r'swedroid\.se/forum/threads/',
        r'forum\.[\w\-]+\.\w+/threads?/',
        r'forums?\.[\w\-]+\.\w+/threads?/',
    ]

    def classify_url(self, url: str) -> str:
        for pattern in self.FORUM_PATTERNS:
            if re.search(pattern, url, re.IGNORECASE):
                return 'forum_thread'
        return 'page'

    def normalize_forum_url(self, url: str) -> Tuple[str, Dict]:
        parsed = urlparse(url)
        path = parsed.path

        thread_id = None
        base_path = path

        if 'swedroid.se/forum/threads' in url:
            thread_match = re.search(r'/threads/[^/]+\.(\d+)', path)
            if thread_match:
                thread_id = thread_match.group(1)

            base_path = re.sub(r'/page-\d+/?$', '/', path)
            if not base_path.endswith('/'):
                base_path += '/'

        base_url = f"{parsed.scheme}://{parsed.netloc}{base_path}"

        metadata = {
            'thread_id': thread_id,
            'original_url': url
        }

        return base_url, metadata

    def get_latest_page_url(self, base_url: str, page_number: int) -> str:
        base_url = base_url.rstrip('/')
        return f"{base_url}/page-{page_number}"
