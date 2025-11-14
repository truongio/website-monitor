from dotenv import load_dotenv
from monitor.forum_parser import ForumThreadParser
import requests

load_dotenv()

parser = ForumThreadParser()

url = "https://swedroid.se/forum/threads/fyndtipstraden-inga-diskussioner.61865/page-290"

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
}

response = requests.get(url, headers=headers)
result = parser.parse_swedroid_thread(response.text, url)

print(f"Total posts parsed: {len(result['posts'])}\n")

if result['posts']:
    first_post = result['posts'][0]
    print("=== First Post ===")
    print(f"Post ID: {first_post['post_id']}")
    print(f"Post Number: {first_post['post_number']}")
    print(f"Author: {first_post['author']}")
    print(f"Timestamp: {first_post['timestamp']}")
    print(f"Permalink: {first_post['permalink']}")
    print(f"\nContent ({len(first_post['content'])} chars):")
    print(first_post['content'])

    if len(result['posts']) > 1:
        print("\n\n=== Second Post ===")
        second_post = result['posts'][1]
        print(f"Post ID: {second_post['post_id']}")
        print(f"Post Number: {second_post['post_number']}")
        print(f"Author: {second_post['author']}")
        print(f"Content preview: {second_post['content'][:100]}...")
