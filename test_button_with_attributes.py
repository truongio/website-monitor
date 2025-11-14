import requests
from monitor.content_cleaner import ContentCleaner

url = "https://www.comviq.se/mobiler/google-pixel-9a/5872/36/SPECIAL_OFFER-46688/24"

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
}

cleaner = ContentCleaner()
selector = 'button[aria-describedby="out-of-stock"]'

print("=== Testing button monitoring WITH attribute capture ===\n")

for attempt in range(3):
    response = requests.get(url, headers=headers)
    content, hash_val = cleaner.process_html_with_selectors(response.text, [selector])
    print(f"Attempt {attempt + 1}:")
    print(f"  Content: {content}")
    print(f"  Hash: {hash_val[:16]}...")
    print()

print("\n=== Simulating state change ===")
print("Current state (disabled):")
print("  Gå till kassan [aria-disabled=true]")
print()
print("When it becomes available (enabled):")
print("  Gå till kassan [aria-disabled=false]")
print("  OR")
print("  Gå till kassan (no aria-disabled attribute)")
print()
print("These would produce DIFFERENT hashes and trigger a notification!")
