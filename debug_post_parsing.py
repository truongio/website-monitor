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

    print("=== First Post Analysis ===")
    print(f"Post ID from element: {first_post.get('id')}")

    # Check for post number anchor
    post_number_elem = first_post.find('a', href=re.compile(r'#post-\d+'))
    if post_number_elem:
        print(f"Post number anchor found: {post_number_elem.get_text()}")
        number_match = re.search(r'#(\d+)', post_number_elem.get_text())
        if number_match:
            print(f"Extracted post number: {number_match.group(1)}")
        else:
            print("Could not extract number from text!")
    else:
        print("Post number anchor NOT found!")

    # Check for author
    author_elem = first_post.find('a', class_=re.compile(r'username'))
    if author_elem:
        print(f"Author found: {author_elem.get_text()}")
    else:
        print("Author NOT found with 'username' class!")

    # Check for content
    content_elem = first_post.find('div', class_=re.compile(r'message-body|bbWrapper'))
    if content_elem:
        content_preview = content_elem.get_text(strip=True)[:100]
        print(f"Content found: {content_preview}...")
    else:
        print("Content NOT found!")
