from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from database import DatabaseClient
from dotenv import load_dotenv
import re


load_dotenv()
db = DatabaseClient()


def is_valid_url(url: str) -> bool:
    url_pattern = re.compile(
        r'^https?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = """
🔍 *Website Monitor Bot*

I'll help you monitor websites and forum threads for changes and notify you when something updates!

*Available Commands:*
/subscribe <url> - Subscribe to a URL or forum thread
/unsubscribe <url> - Unsubscribe from a URL
/list - Show your subscriptions
/pause <url> - Pause monitoring a URL
/resume <url> - Resume monitoring a URL
/help - Show this help message

*Examples:*
`/subscribe https://example.com/news` - Monitor page changes
`/subscribe https://forum.com/thread/123` - Monitor new forum posts

For regular pages, I'll notify you when content changes.
For forum threads, I'll notify you only about NEW POSTS with author, content, and link!
    """
    await update.message.reply_text(welcome_message, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start_command(update, context)


async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or len(context.args) < 1:
        await update.message.reply_text(
            "❌ Please provide a URL to subscribe to.\n\n"
            "Usage: `/subscribe https://example.com`",
            parse_mode='Markdown'
        )
        return

    url = context.args[0]

    if not is_valid_url(url):
        await update.message.reply_text("❌ Invalid URL. Please provide a valid HTTP/HTTPS URL.")
        return

    try:
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id

        db.add_subscription(user_id, chat_id, url)

        await update.message.reply_text(
            f"✅ Successfully subscribed to:\n`{url}`\n\n"
            f"I'll notify you when this page changes!",
            parse_mode='Markdown'
        )
    except Exception as e:
        print(f"Error subscribing to [{url}]: {e}")
        await update.message.reply_text(
            "❌ Failed to subscribe. Please try again later."
        )


async def unsubscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or len(context.args) < 1:
        await update.message.reply_text(
            "❌ Please provide a URL to unsubscribe from.\n\n"
            "Usage: `/unsubscribe https://example.com`",
            parse_mode='Markdown'
        )
        return

    url = context.args[0]
    user_id = update.effective_user.id

    try:
        success = db.remove_subscription(user_id, url)

        if success:
            await update.message.reply_text(
                f"✅ Successfully unsubscribed from:\n`{url}`",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                "❌ You are not subscribed to this URL."
            )
    except Exception as e:
        print(f"Error unsubscribing from [{url}]: {e}")
        await update.message.reply_text(
            "❌ Failed to unsubscribe. Please try again later."
        )


async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    try:
        subscriptions = db.get_user_subscriptions(user_id)

        if not subscriptions:
            await update.message.reply_text(
                "📭 You have no active subscriptions.\n\n"
                "Use `/subscribe <url>` to start monitoring a website!",
                parse_mode='Markdown'
            )
            return

        message = "📋 *Your Subscriptions:*\n\n"
        for sub in subscriptions:
            status_emoji = "✅" if sub['status'] == 'active' else "⏸️"
            message += f"{status_emoji} `{sub['url']}` ({sub['status']})\n"

        message += f"\n*Total:* {len(subscriptions)} subscription(s)"

        await update.message.reply_text(message, parse_mode='Markdown')
    except Exception as e:
        print(f"Error listing subscriptions: {e}")
        await update.message.reply_text(
            "❌ Failed to retrieve subscriptions. Please try again later."
        )


async def pause_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or len(context.args) < 1:
        await update.message.reply_text(
            "❌ Please provide a URL to pause.\n\n"
            "Usage: `/pause https://example.com`",
            parse_mode='Markdown'
        )
        return

    url = context.args[0]
    user_id = update.effective_user.id

    try:
        success = db.update_subscription_status(user_id, url, 'paused')

        if success:
            await update.message.reply_text(
                f"⏸️ Paused monitoring for:\n`{url}`",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                "❌ Subscription not found or already paused."
            )
    except Exception as e:
        print(f"Error pausing subscription for [{url}]: {e}")
        await update.message.reply_text(
            "❌ Failed to pause subscription. Please try again later."
        )


async def resume_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or len(context.args) < 1:
        await update.message.reply_text(
            "❌ Please provide a URL to resume.\n\n"
            "Usage: `/resume https://example.com`",
            parse_mode='Markdown'
        )
        return

    url = context.args[0]
    user_id = update.effective_user.id

    try:
        success = db.update_subscription_status(user_id, url, 'active')

        if success:
            await update.message.reply_text(
                f"▶️ Resumed monitoring for:\n`{url}`",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                "❌ Subscription not found or already active."
            )
    except Exception as e:
        print(f"Error resuming subscription for [{url}]: {e}")
        await update.message.reply_text(
            "❌ Failed to resume subscription. Please try again later."
        )


def setup_handlers(application):
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("subscribe", subscribe_command))
    application.add_handler(CommandHandler("unsubscribe", unsubscribe_command))
    application.add_handler(CommandHandler("list", list_command))
    application.add_handler(CommandHandler("pause", pause_command))
    application.add_handler(CommandHandler("resume", resume_command))
