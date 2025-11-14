import requests
import re
from bs4 import BeautifulSoup

url = "https://swedroid.se/forum/threads/fyndtipstraden-inga-diskussioner.61865/page-290"

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'lxml')

post_elements = soup.find_all('li', class_=re.compile(r'message'))
print(f"Found {len(post_elements)} posts\n")

if post_elements:
    first_post = post_elements[0]

    print("=== First Post Content Extraction ===")
    print(f"Post ID: {first_post.get('id')}")

    # Try the current pattern
    content_elem = first_post.find('div', class_=re.compile(r'message-body|bbWrapper'))
    if content_elem:
        content = content_elem.get_text(separator=' ', strip=True)
        print(f"\nCurrent pattern found content ({len(content)} chars):")
        print(f"{content[:200]}...")
    else:
        print("\n❌ Current pattern (message-body|bbWrapper) found NO content!")

    # Try to find all divs with any class containing 'message'
    print("\n\nAll divs with 'message' in class:")
    message_divs = first_post.find_all('div', class_=re.compile(r'message'))
    for div in message_divs[:5]:
        classes = div.get('class', [])
        text_preview = div.get_text(strip=True)[:50]
        print(f"  Classes: {classes} | Text: {text_preview}...")

    # Try to find divs with 'bb' in class
    print("\n\nAll divs with 'bb' in class:")
    bb_divs = first_post.find_all('div', class_=re.compile(r'bb'))
    for div in bb_divs[:5]:
        classes = div.get('class', [])
        text_preview = div.get_text(strip=True)[:50]
        print(f"  Classes: {classes} | Text: {text_preview}...")
