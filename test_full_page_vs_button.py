import requests
from monitor.content_cleaner import ContentCleaner
import time

url = "https://www.comviq.se/mobiler/google-pixel-9a/5872/36/SPECIAL_OFFER-46688/24"

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
}

cleaner = ContentCleaner()
button_selector = 'button[aria-describedby="out-of-stock"]'

print("=== Comparing full page vs button-only monitoring ===\n")

# First fetch
print("First fetch:")
response1 = requests.get(url, headers=headers)
full_content1, full_hash1 = cleaner.process_html(response1.text)
button_content1, button_hash1 = cleaner.process_html_with_selectors(response1.text, [button_selector])

print(f"  Full page hash: {full_hash1[:16]}...")
print(f"  Button hash: {button_hash1[:16]}...")
print(f"  Button content: {button_content1}")

print("\nWaiting 3 seconds...\n")
time.sleep(3)

# Second fetch
print("Second fetch:")
response2 = requests.get(url, headers=headers)
full_content2, full_hash2 = cleaner.process_html(response2.text)
button_content2, button_hash2 = cleaner.process_html_with_selectors(response2.text, [button_selector])

print(f"  Full page hash: {full_hash2[:16]}...")
print(f"  Button hash: {button_hash2[:16]}...")
print(f"  Button content: {button_content2}")

print("\n=== Results ===")
print(f"Full page changed: {full_hash1 != full_hash2}")
print(f"Button changed: {button_hash1 != button_hash2}")

if button_hash1 != button_hash2:
    print("\n❌ WARNING: Button hash changed between fetches!")
    print(f"  Before: {button_content1}")
    print(f"  After: {button_content2}")
    print("\nThis means there's dynamic content in the button that changes on each page load.")
else:
    print("\n✅ Button hash is stable - no false positives expected!")
