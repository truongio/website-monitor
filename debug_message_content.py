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

if post_elements:
    first_post = post_elements[0]
    print(f"Post ID: {first_post.get('id')}\n")

    # Find messageContent
    message_content = first_post.find('div', class_='messageContent')
    if message_content:
        print("Found messageContent div!")

        # Look inside for the actual message text container
        print("\nDirect children:")
        for child in message_content.children:
            if hasattr(child, 'name') and child.name:
                classes = child.get('class', [])
                text_preview = child.get_text(strip=True)[:80]
                print(f"  <{child.name}> classes={classes} | {text_preview}...")

        # Get full text
        full_text = message_content.get_text(separator=' ', strip=True)
        print(f"\nFull content ({len(full_text)} chars):")
        print(full_text[:300])
