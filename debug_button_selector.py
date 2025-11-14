import requests
from bs4 import BeautifulSoup
from monitor.content_cleaner import ContentCleaner

url = "https://www.comviq.se/mobiler/google-pixel-9a/5872/36/SPECIAL_OFFER-46688/24"

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
}

print("=== Testing button selector ===\n")

# Fetch the page
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'lxml')

# Test the selector
selector = 'button[aria-describedby="out-of-stock"]'
buttons = soup.select(selector)

print(f"Selector: {selector}")
print(f"Found {len(buttons)} button(s)\n")

for i, btn in enumerate(buttons):
    print(f"Button {i+1}:")
    print(f"  aria-disabled: {btn.get('aria-disabled')}")
    print(f"  aria-describedby: {btn.get('aria-describedby')}")
    print(f"  type: {btn.get('type')}")
    print(f"  classes: {btn.get('class')}")
    text = btn.get_text(strip=True)
    print(f"  text: {text}")
    print(f"  Full HTML preview: {str(btn)[:200]}...")
    print()

# Test with ContentCleaner
print("\n=== Testing with ContentCleaner (simulating monitoring) ===\n")

cleaner = ContentCleaner()

# Run multiple times to see if hash changes
for attempt in range(3):
    response = requests.get(url, headers=headers)
    content, hash_val = cleaner.process_html_with_selectors(response.text, [selector])
    print(f"Attempt {attempt + 1}:")
    print(f"  Content: {content[:150]}")
    print(f"  Hash: {hash_val[:16]}...")
    print()

print("\n=== Testing all submit buttons ===\n")

all_submit_buttons = soup.select('button[type="submit"]')
print(f"Total submit buttons found: {len(all_submit_buttons)}\n")

for i, btn in enumerate(all_submit_buttons[:5]):
    text = btn.get_text(strip=True)
    aria_disabled = btn.get('aria-disabled')
    aria_describedby = btn.get('aria-describedby')
    print(f"{i+1}. Text: '{text}' | aria-disabled: {aria_disabled} | aria-describedby: {aria_describedby}")
