import requests
from bs4 import BeautifulSoup

url = "https://swedroid.se/forum/threads/fyndtipstraden-inga-diskussioner.61865/page-290"

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'lxml')

# Try to find posts
articles = soup.find_all('article')
print(f"Found {len(articles)} <article> tags")

lis = soup.find_all('li', class_=lambda x: x and 'message' in x if x else False)
print(f"Found {len(lis)} <li> tags with 'message' class")

# Look for post anchors
post_anchors = soup.find_all('a', href=lambda x: x and '#post-' in x if x else False)
print(f"Found {len(post_anchors)} post anchor links")

if post_anchors:
    print("\nFirst few post anchors:")
    for anchor in post_anchors[:3]:
        print(f"  Text: {anchor.get_text()}, href: {anchor.get('href')}")

# Try finding any element with post- in id
post_ids = soup.find_all(id=lambda x: x and 'post-' in x if x else False)
print(f"\nFound {len(post_ids)} elements with 'post-' in ID")

if post_ids:
    print("\nFirst post element:")
    first_post = post_ids[0]
    print(f"  Tag: {first_post.name}")
    print(f"  ID: {first_post.get('id')}")
    print(f"  Classes: {first_post.get('class')}")
