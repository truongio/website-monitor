import re

test_urls = [
    "https://swedroid.se/forum/threads/fyndtipstraden-inga-diskussioner.61865/page-290",
    "https://swedroid.se/forum/threads/fyndtipstraden-inga-diskussioner.61865/",
    "https://swedroid.se/forum/threads/fyndtipstraden-inga-diskussioner.61865"
]

for url in test_urls:
    print(f"\nOriginal: {url}")

    # Remove trailing /
    clean = url.rstrip('/')
    print(f"After rstrip('/'): {clean}")

    # Remove page suffix
    base_without_page = re.sub(r'/page-\d+$', '', clean)
    print(f"After removing /page-N: {base_without_page}")
