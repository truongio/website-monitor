import requests
from typing import Optional, Dict
from .content_cleaner import ContentCleaner


class PageChecker:
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.cleaner = ContentCleaner()
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

    def check_page(self, url: str, previous_hash: Optional[str] = None) -> Dict:
        html = self.fetch_page(url)

        if html is None:
            return {
                'success': False,
                'error': 'Failed to fetch page',
                'url': url
            }

        cleaned_content, content_hash = self.cleaner.process_html(html)

        snippet = cleaned_content[:500] if cleaned_content else ''

        changed = previous_hash is not None and previous_hash != content_hash

        return {
            'success': True,
            'url': url,
            'content_hash': content_hash,
            'changed': changed,
            'previous_hash': previous_hash,
            'snippet': snippet
        }
