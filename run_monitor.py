import os
import asyncio
from dotenv import load_dotenv
from telegram import Bot
from database import DatabaseClient
from monitor import PageChecker
from collections import defaultdict


load_dotenv()


async def send_page_notification(bot: Bot, chat_id: int, url: str, snippet: str):
    message = (
        f"🔔 *Page Changed!*\n\n"
        f"[View Page]({url})\n\n"
        f"Preview:\n{snippet[:300]}..."
    )
    try:
        await bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode='Markdown',
            disable_web_page_preview=False
        )
        print(f"Sent page notification to chat [{chat_id}] for [{url}]")
    except Exception as e:
        print(f"Failed to send notification to chat [{chat_id}]: {e}")


async def send_forum_notification(bot: Bot, chat_id: int, url: str, new_posts: list):
    if not new_posts:
        return

    message = f"🆕 *New Forum Post{'s' if len(new_posts) > 1 else ''}!*\n\n"

    for post in new_posts[:5]:
        author = post.get('author', 'Unknown')
        post_number = post.get('post_number', '?')
        content = post.get('content', '')
        permalink = post.get('permalink', url)

        content_preview = content[:200] if content else 'No content'
        if len(content) > 200:
            content_preview += '...'

        message += f"*{author}* (#{post_number})\n"
        message += f"{content_preview}\n"
        message += f"[View Post]({permalink})\n\n"

    if len(new_posts) > 5:
        message += f"_...and {len(new_posts) - 5} more post(s)_\n"

    try:
        await bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode='Markdown',
            disable_web_page_preview=True
        )
        print(f"Sent forum notification to chat [{chat_id}] for [{url}] ({len(new_posts)} new posts)")
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

        if previous_state and 'selectors' not in previous_state and subs:
            previous_state['selectors'] = subs[0].get('selectors')

        result = checker.check_page(url, previous_state)

        if not result['success']:
            print(f"Failed to check [{url}]: {result.get('error')}")
            continue

        monitoring_type = result.get('monitoring_type', 'page')

        if monitoring_type == 'forum_thread':
            highest_post_number = result.get('highest_post_number')
            metadata = result.get('metadata', {})

            db.update_forum_thread_state(
                url,
                highest_post_number,
                metadata=metadata
            )

            if result['changed']:
                new_posts = result.get('new_posts', [])
                print(f"New posts detected for [{url}]! {len(new_posts)} new post(s). Notifying {len(subs)} subscriber(s)...")

                for sub in subs:
                    await send_forum_notification(
                        bot,
                        sub['chat_id'],
                        url,
                        new_posts
                    )
            else:
                print(f"No new posts for [{url}]")
        else:
            selectors = result.get('selectors')
            db.update_page_state(
                url,
                result['content_hash'],
                result['snippet'],
                selectors
            )

            if result['changed']:
                print(f"Change detected for [{url}]! Notifying {len(subs)} subscriber(s)...")

                for sub in subs:
                    await send_page_notification(
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
