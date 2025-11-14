from dotenv import load_dotenv
from monitor.checker import PageChecker

load_dotenv()

checker = PageChecker()

url = "https://swedroid.se/forum/threads/fyndtipstraden-inga-diskussioner.61865/page-290"

print(f"Testing forum parser on: {url}\n")

result = checker.check_page(url, None)

print(f"Success: {result.get('success')}")
print(f"Monitoring type: {result.get('monitoring_type')}")
print(f"Highest post number: {result.get('highest_post_number')}")
print(f"Total posts on page: {result.get('total_posts_on_page')}")
print(f"Metadata: {result.get('metadata')}")
print(f"Changed: {result.get('changed')}")
print(f"New posts: {len(result.get('new_posts', []))}")

if result.get('total_posts_on_page') == 0:
    print("\n❌ No posts found! Parser might be broken.")
