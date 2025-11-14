from monitor.url_classifier import URLClassifier

classifier = URLClassifier()

# Mock subscriptions with different types
subscriptions = [
    {
        'url': 'https://swedroid.se/forum/threads/fyndtipstraden-inga-diskussioner.61865/page-290',
        'status': 'active',
        'selectors': None
    },
    {
        'url': 'https://www.comviq.se/mobiler/google-pixel-9a/5872/36/SPECIAL_OFFER-46688/24',
        'status': 'active',
        'selectors': ['button span.x9o0bqe', '.price']
    },
    {
        'url': 'https://news.ycombinator.com/',
        'status': 'active',
        'selectors': None
    },
    {
        'url': 'https://example.com/product',
        'status': 'paused',
        'selectors': ['.availability', '.price', '.stock-status']
    }
]

print("📋 *Your Subscriptions:*\n")

for sub in subscriptions:
    status_emoji = "✅" if sub['status'] == 'active' else "⏸️"

    # Determine subscription type
    url_type = classifier.classify_url(sub['url'])
    selectors = sub.get('selectors')

    if url_type == 'forum_thread':
        type_icon = "🧵"
        type_label = "Forum"
    elif selectors:
        type_icon = "🎯"
        type_label = f"Targeted ({len(selectors)} selector{'s' if len(selectors) > 1 else ''})"
    else:
        type_icon = "📄"
        type_label = "Page"

    print(f"{status_emoji} {type_icon} *{type_label}*")
    print(f"   `{sub['url']}`")

    if selectors:
        selector_preview = ', '.join([f"`{s}`" for s in selectors[:2]])
        if len(selectors) > 2:
            selector_preview += f" +{len(selectors) - 2} more"
        print(f"   Watching: {selector_preview}")

    print()

print(f"\n*Total:* {len(subscriptions)} subscription(s)")
