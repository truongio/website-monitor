import requests
import re
from bs4 import BeautifulSoup

url = "https://swedroid.se/forum/threads/fyndtipstraden-inga-diskussioner.61865/page-290"

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'lxml')

first_post = soup.find('li', id='post-3164190')

if first_post:
    print("All anchors with #post- in href:")
    anchors = first_post.find_all('a', href=re.compile(r'#post-'))
    for anchor in anchors:
        print(f"  Text: '{anchor.get_text()}' | href: {anchor.get('href')}")

    print("\n\nNow searching specifically for text containing #:")
    all_anchors = first_post.find_all('a')
    for anchor in all_anchors:
        text = anchor.get_text(strip=True)
        if '#' in text:
            print(f"  Text: '{text}' | href: {anchor.get('href')}")
