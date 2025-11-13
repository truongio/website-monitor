import requests
from typing import Optional, Dict
from .content_cleaner import ContentCleaner
from .url_classifier import URLClassifier
from .forum_parser import ForumThreadParser


class PageChecker:
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.cleaner = ContentCleaner()
        self.classifier = URLClassifier()
        self.forum_parser = ForumThreadParser()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    def fetch_page(self, url: str) -> Optional[str]:
        try:
            response = requests.get(
                url,
                timeout=self.timeout,
                headers=self.headers,
                allow_redirects=True
            )
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching [{url}]: {e}")
            return None

    def check_page(self, url: str, previous_state: Optional[Dict] = None) -> Dict:
        url_type = self.classifier.classify_url(url)

        if url_type == 'forum_thread':
            return self._check_forum_thread(url, previous_state)
        else:
            return self._check_regular_page(url, previous_state)

    def _check_regular_page(self, url: str, previous_state: Optional[Dict] = None) -> Dict:
        previous_hash = previous_state.get('content_hash') if previous_state else None

        html = self.fetch_page(url)

        if html is None:
            return {
                'success': False,
                'error': 'Failed to fetch page',
                'url': url,
                'monitoring_type': 'page'
            }

        cleaned_content, content_hash = self.cleaner.process_html(html)

        snippet = cleaned_content[:500] if cleaned_content else ''

        changed = previous_hash is not None and previous_hash != content_hash

        return {
            'success': True,
            'url': url,
            'monitoring_type': 'page',
            'content_hash': content_hash,
            'changed': changed,
            'previous_hash': previous_hash,
            'snippet': snippet
        }

    def _check_forum_thread(self, url: str, previous_state: Optional[Dict] = None) -> Dict:
        base_url, metadata = self.classifier.normalize_forum_url(url)

        html = self.fetch_page(url)

        if html is None:
            return {
                'success': False,
                'error': 'Failed to fetch page',
                'url': url,
                'monitoring_type': 'forum_thread'
            }

        thread_data = self.forum_parser.parse_swedroid_thread(html, base_url)

        posts = thread_data['posts']
        current_page = thread_data['current_page']
        total_pages = thread_data['total_pages']

        if current_page < total_pages:
            latest_page_url = self.classifier.get_latest_page_url(base_url, total_pages)
            print(f"Not on latest page. Fetching page {total_pages}...")
            html = self.fetch_page(latest_page_url)
            if html:
                thread_data = self.forum_parser.parse_swedroid_thread(html, base_url)
                posts = thread_data['posts']

        highest_post_number = self.forum_parser.get_highest_post_number(posts)

        previous_post_number = None
        if previous_state:
            previous_post_number = previous_state.get('last_post_number')

        new_posts = []
        changed = False

        if previous_post_number is not None:
            new_posts = self.forum_parser.get_new_posts(posts, previous_post_number)
            changed = len(new_posts) > 0
        else:
            print(f"First check for forum thread. Storing baseline post #{highest_post_number}")

        return {
            'success': True,
            'url': url,
            'monitoring_type': 'forum_thread',
            'changed': changed,
            'new_posts': new_posts,
            'highest_post_number': highest_post_number,
            'total_posts_on_page': len(posts),
            'metadata': {
                **metadata,
                'current_page': thread_data['current_page'],
                'total_pages': thread_data['total_pages']
            }
        }
