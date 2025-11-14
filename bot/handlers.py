from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from database import DatabaseClient
from monitor.url_classifier import URLClassifier
from dotenv import load_dotenv
import re


load_dotenv()
db = DatabaseClient()
classifier = URLClassifier()


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
/watch <url> <selector1> <selector2> ... - Monitor specific elements
/unsubscribe <url> - Unsubscribe from a URL
/list - Show your subscriptions
/pause <url> - Pause monitoring a URL
/resume <url> - Resume monitoring a URL
/help - Show this help message

*Examples:*
`/subscribe https://example.com/news` - Monitor entire page
`/watch https://shop.com/product button.buy-button .price` - Monitor button & price only
`/subscribe https://forum.com/thread/123` - Monitor new forum posts

For regular pages, I'll notify you when content changes.
For targeted monitoring with /watch, only specified elements are tracked (reduces false positives!).
For forum threads, I'll notify you only about NEW POSTS with author, content, and link!
    """
    await update.message.reply_text(welcome_message, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start_command(update, context)


async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

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

        url_type = classifier.classify_url(url)

        if url_type == 'forum_thread':
            type_message = "🧵 *Detected as: Forum Thread*\nI'll notify you about NEW POSTS only (not existing ones)."
        else:
            type_message = "📄 *Detected as: Regular Page*\nI'll notify you when content changes."

        await update.message.reply_text(
            f"✅ Successfully subscribed to:\n`{url}`\n\n"
            f"{type_message}",
            parse_mode='Markdown'
        )
    except Exception as e:
        print(f"Error subscribing to [{url}]: {e}")
        if update.message:
            await update.message.reply_text(
                "❌ Failed to subscribe. Please try again later."
            )


async def watch_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "❌ Please provide a URL and at least one CSS selector.\n\n"
            "Usage: `/watch https://example.com .button .price`\n\n"
            "*Examples:*\n"
            "`/watch https://shop.com/product button.checkout`\n"
            "`/watch https://site.com .price .availability`\n\n"
            "This will only monitor the specified elements, reducing false positives!",
            parse_mode='Markdown'
        )
        return

    url = context.args[0]
    selectors = context.args[1:]

    if not is_valid_url(url):
        await update.message.reply_text("❌ Invalid URL. Please provide a valid HTTP/HTTPS URL.")
        return

    try:
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id

        db.add_subscription(user_id, chat_id, url, selectors)

        selector_list = '\n'.join([f"  • `{s}`" for s in selectors])

        await update.message.reply_text(
            f"✅ Successfully subscribed with targeted monitoring:\n\n"
            f"URL: `{url}`\n\n"
            f"Monitoring these elements:\n{selector_list}\n\n"
            f"🎯 *Targeted Mode*: I'll only notify you when these specific elements change!",
            parse_mode='Markdown'
        )
    except Exception as e:
        print(f"Error creating watch subscription for [{url}]: {e}")
        if update.message:
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

            message += f"{status_emoji} {type_icon} *{type_label}*\n"
            message += f"   `{sub['url']}`\n"

            if selectors:
                selector_preview = ', '.join([f"`{s}`" for s in selectors[:2]])
                if len(selectors) > 2:
                    selector_preview += f" +{len(selectors) - 2} more"
                message += f"   Watching: {selector_preview}\n"

            message += "\n"

        message += f"*Total:* {len(subscriptions)} subscription(s)"

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
    application.add_handler(CommandHandler("watch", watch_command))
    application.add_handler(CommandHandler("unsubscribe", unsubscribe_command))
    application.add_handler(CommandHandler("list", list_command))
    application.add_handler(CommandHandler("pause", pause_command))
    application.add_handler(CommandHandler("resume", resume_command))
