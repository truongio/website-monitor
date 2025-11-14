import requests
from bs4 import BeautifulSoup

url = "https://www.comviq.se/mobiler/google-pixel-9a/5872/36/SPECIAL_OFFER-46688/24"

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'lxml')

print("=== Searching for button ===")
buttons = soup.find_all('button')
print(f"Found {len(buttons)} buttons\n")

for i, btn in enumerate(buttons[:5]):
    text = btn.get_text(strip=True)
    classes = btn.get('class', [])
    disabled = btn.get('disabled')
    print(f"Button {i+1}:")
    print(f"  Text: {text}")
    print(f"  Classes: {classes}")
    print(f"  Disabled: {disabled}")
    print()

print("\n=== Searching for 'Tillfälligt slut' ===")
stock_elements = soup.find_all(string=lambda text: 'Tillfälligt slut' in text if text else False)
print(f"Found {len(stock_elements)} elements with 'Tillfälligt slut'")
for elem in stock_elements[:3]:
    parent = elem.parent
    print(f"  Parent tag: {parent.name}, classes: {parent.get('class', [])}")

print("\n=== Searching for 'Gå till kassan' ===")
checkout_elements = soup.find_all(string=lambda text: 'Gå till kassan' in text if text else False)
print(f"Found {len(checkout_elements)} elements with 'Gå till kassan'")
for elem in checkout_elements[:3]:
    parent = elem.parent
    print(f"  Parent tag: {parent.name}, classes: {parent.get('class', [])}")
    print(f"  Disabled: {parent.get('disabled')}")

print("\n=== Searching for price ===")
price_pattern = soup.find_all(string=lambda text: 'kr/mån' in text if text else False)
print(f"Found {len(price_pattern)} elements with 'kr/mån'")
for elem in price_pattern[:3]:
    print(f"  Text: {elem.strip()}")
