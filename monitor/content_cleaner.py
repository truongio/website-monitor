import re
import hashlib
from bs4 import BeautifulSoup, Comment
from typing import Optional


class ContentCleaner:
    DYNAMIC_PATTERNS = [
        r'\d{4}-\d{2}-\d{2}',
        r'\d{2}:\d{2}:\d{2}',
        r'\d{13}',
        r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
    ]

    AD_SELECTORS = [
        '[class*="ad-"]',
        '[class*="advertisement"]',
        '[id*="ad-"]',
        '[id*="advertisement"]',
        '.ad',
        '.ads',
        '.adsbygoogle',
        'iframe[src*="doubleclick"]',
        'iframe[src*="googlesyndication"]',
    ]

    SOCIAL_SELECTORS = [
        '[class*="social"]',
        '[class*="share"]',
        '[class*="twitter"]',
        '[class*="facebook"]',
        '[class*="linkedin"]',
        '.fb-like',
        '.twitter-share',
    ]

    def clean_content(self, html: str) -> str:
        soup = BeautifulSoup(html, 'lxml')

        for element in soup(['script', 'style', 'noscript', 'iframe']):
            element.decompose()

        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()

        for selector in self.AD_SELECTORS + self.SOCIAL_SELECTORS:
            for element in soup.select(selector):
                element.decompose()

        text = soup.get_text(separator=' ', strip=True)

        for pattern in self.DYNAMIC_PATTERNS:
            text = re.sub(pattern, '', text)

        text = re.sub(r'\s+', ' ', text)
        text = text.strip()

        return text

    def generate_hash(self, content: str) -> str:
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def process_html(self, html: str) -> tuple[str, str]:
        cleaned_content = self.clean_content(html)
        content_hash = self.generate_hash(cleaned_content)
        return cleaned_content, content_hash

    def process_html_with_selectors(self, html: str, selectors: list) -> tuple[str, str]:
        soup = BeautifulSoup(html, 'lxml')

        selected_texts = []

        # Attributes that indicate state changes (important for buttons, forms, etc.)
        state_attributes = ['disabled', 'aria-disabled', 'aria-checked', 'aria-selected',
                           'aria-expanded', 'checked', 'selected', 'readonly']

        for selector in selectors:
            elements = soup.select(selector)
            for elem in elements:
                for script_style in elem(['script', 'style', 'noscript']):
                    script_style.decompose()

                # Get text content
                text = elem.get_text(separator=' ', strip=True)
                text = re.sub(r'\s+', ' ', text).strip()

                # Capture important state attributes
                attrs = []
                for attr in state_attributes:
                    if elem.has_attr(attr):
                        attrs.append(f"{attr}={elem.get(attr)}")

                # Combine text with attributes
                if text or attrs:
                    if attrs:
                        element_signature = f"{text} [{' '.join(attrs)}]"
                    else:
                        element_signature = text
                    selected_texts.append(element_signature)

        combined_text = ' | '.join(selected_texts)

        content_hash = self.generate_hash(combined_text)
        return combined_text, content_hash
