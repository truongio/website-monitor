from dotenv import load_dotenv
from monitor.checker import PageChecker
from monitor.content_cleaner import ContentCleaner
import requests
from bs4 import BeautifulSoup

load_dotenv()

url = "https://www.comviq.se/mobiler/google-pixel-9a/5872/36/SPECIAL_OFFER-46688/24"

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'lxml')

print("=== Testing potential selectors ===\n")

test_selectors = [
    'button:contains("Gå till kassan")',
    'button',
    '.x9o0bqe',
    'button[disabled]',
    '[class*="temporarily"]',
    '[class*="sold"]',
    '[class*="stock"]'
]

for selector in test_selectors:
    try:
        if ':contains' in selector:
            print(f"\nTesting {selector}:")
            print("  (Can't test :contains with BeautifulSoup, but CSS will support it)")
            continue

        elements = soup.select(selector)
        print(f"\nTesting {selector}:")
        print(f"  Found {len(elements)} elements")
        if elements and len(elements) < 10:
            for i, elem in enumerate(elements[:3]):
                text = elem.get_text(strip=True)[:80]
                disabled = elem.get('disabled')
                print(f"    [{i+1}] {text}... (disabled={disabled})")
    except Exception as e:
        print(f"  Error: {e}")

print("\n\n=== Testing selector-based monitoring ===\n")

cleaner = ContentCleaner()

# Test with button selectors
selectors = ['button span.x9o0bqe']
content, hash1 = cleaner.process_html_with_selectors(response.text, selectors)
print(f"Selector: {selectors}")
print(f"Content extracted: {content[:200]}")
print(f"Hash: {hash1[:16]}...")

print("\n\n=== Full page check with selectors ===\n")

checker = PageChecker()

# Test without selectors (baseline)
result1 = checker.check_page(url, None)
print(f"Without selectors - Hash: {result1['content_hash'][:16]}...")

# Test with selectors
result2 = checker.check_page(url, {'selectors': selectors})
print(f"With selectors {selectors} - Hash: {result2['content_hash'][:16]}...")
print(f"Content: {result2['snippet'][:150]}...")
