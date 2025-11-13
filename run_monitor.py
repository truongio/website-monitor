import os
import asyncio
from dotenv import load_dotenv
from telegram import Bot
from database import DatabaseClient
from monitor import PageChecker
from collections import defaultdict


load_dotenv()


async def send_notification(bot: Bot, chat_id: int, url: str, snippet: str):
    message = (
        f"🔔 *Page Changed!*\n\n"
        f"URL: `{url}`\n\n"
        f"Preview:\n{snippet[:300]}..."
    )
    try:
        await bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode='Markdown'
        )
        print(f"Sent notification to chat [{chat_id}] for [{url}]")
    except Exception as e:
        print(f"Failed to send notification to chat [{chat_id}]: {e}")


async def monitor_pages():
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not telegram_token:
        raise ValueError("TELEGRAM_BOT_TOKEN is required")

    db = DatabaseClient()
    checker = PageChecker()
    bot = Bot(token=telegram_token)

    print("Fetching active subscriptions...")
    subscriptions = db.get_active_subscriptions()

    if not subscriptions:
        print("No active subscriptions found")
        return

    url_to_subs = defaultdict(list)
    for sub in subscriptions:
        url_to_subs[sub['url']].append(sub)

    print(f"Checking {len(url_to_subs)} unique URLs...")

    for url, subs in url_to_subs.items():
        print(f"Checking [{url}]...")

        previous_state = db.get_page_state(url)
        previous_hash = previous_state['content_hash'] if previous_state else None

        result = checker.check_page(url, previous_hash)

        if not result['success']:
            print(f"Failed to check [{url}]: {result.get('error')}")
            continue

        db.update_page_state(
            url,
            result['content_hash'],
            result['snippet']
        )

        if result['changed']:
            print(f"Change detected for [{url}]! Notifying {len(subs)} subscriber(s)...")

            for sub in subs:
                await send_notification(
                    bot,
                    sub['chat_id'],
                    url,
                    result['snippet']
                )
        else:
            print(f"No change detected for [{url}]")

    print("Monitoring complete!")


if __name__ == '__main__':
    asyncio.run(monitor_pages())
