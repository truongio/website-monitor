import re
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from datetime import datetime


class ForumThreadParser:
    def parse_swedroid_thread(self, html: str, base_url: str) -> Dict:
        soup = BeautifulSoup(html, 'lxml')
        posts = []

        post_elements = soup.find_all('article', class_=re.compile(r'message'))
        if not post_elements:
            post_elements = soup.find_all('li', class_=re.compile(r'message'))

        for post_elem in post_elements:
            try:
                post_data = self._extract_post_data(post_elem, base_url)
                if post_data:
                    posts.append(post_data)
            except Exception as e:
                print(f"Error parsing post: {e}")
                continue

        current_page, total_pages = self._extract_pagination(soup)

        thread_id = self._extract_thread_id(base_url)

        return {
            'posts': posts,
            'current_page': current_page,
            'total_pages': total_pages,
            'thread_id': thread_id
        }

    def _extract_post_data(self, post_elem, base_url: str) -> Optional[Dict]:
        post_id = post_elem.get('id')
        if not post_id:
            data_content = post_elem.get('data-content')
            if data_content:
                post_id = data_content

        post_number = None
        post_number_elems = post_elem.find_all('a', href=re.compile(r'#post-\d+'))
        for elem in post_number_elems:
            number_text = elem.get_text(strip=True)
            if '#' in number_text:
                number_match = re.search(r'#(\d+)', number_text)
                if number_match:
                    post_number = int(number_match.group(1))
                    break

        author = None
        author_elem = post_elem.find('a', class_=re.compile(r'username'))
        if not author_elem:
            author_elem = post_elem.find('h4', class_=re.compile(r'message-name'))
            if author_elem:
                author_link = author_elem.find('a')
                if author_link:
                    author = author_link.get_text(strip=True)
        else:
            author = author_elem.get_text(strip=True)

        timestamp_elem = post_elem.find('time')
        timestamp = None
        if timestamp_elem:
            datetime_attr = timestamp_elem.get('datetime')
            if datetime_attr:
                timestamp = datetime_attr
            else:
                timestamp = timestamp_elem.get_text(strip=True)

        content_elem = post_elem.find('div', class_=re.compile(r'message-body|bbWrapper'))
        content = ''
        if content_elem:
            content = content_elem.get_text(separator=' ', strip=True)
            content = re.sub(r'\s+', ' ', content)

        permalink = None
        if post_id:
            permalink = f"{base_url}#{post_id}"

        if not post_id or not post_number:
            return None

        return {
            'post_id': post_id,
            'post_number': post_number,
            'author': author or 'Unknown',
            'timestamp': timestamp or '',
            'content': content,
            'permalink': permalink
        }

    def _extract_pagination(self, soup: BeautifulSoup) -> tuple:
        current_page = 1
        total_pages = 1

        page_nav = soup.find('div', class_=re.compile(r'pageNav'))
        if page_nav:
            page_text = page_nav.get_text()
            page_match = re.search(r'Sida\s+(\d+)\s+av\s+(\d+)', page_text)
            if not page_match:
                page_match = re.search(r'Page\s+(\d+)\s+of\s+(\d+)', page_text)

            if page_match:
                current_page = int(page_match.group(1))
                total_pages = int(page_match.group(2))

        return current_page, total_pages

    def _extract_thread_id(self, url: str) -> Optional[str]:
        thread_match = re.search(r'threads/[^/]+\.(\d+)', url)
        if thread_match:
            return thread_match.group(1)
        return None

    def get_new_posts(self, all_posts: List[Dict], last_post_number: Optional[int]) -> List[Dict]:
        if last_post_number is None:
            return []

        new_posts = [
            post for post in all_posts
            if post['post_number'] > last_post_number
        ]

        new_posts.sort(key=lambda x: x['post_number'])

        return new_posts

    def get_highest_post_number(self, posts: List[Dict]) -> Optional[int]:
        if not posts:
            return None

        return max(post['post_number'] for post in posts)
