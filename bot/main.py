import os
from dotenv import load_dotenv
from telegram.ext import Application
from .handlers import setup_handlers


load_dotenv()


def run_bot():
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")

    application = Application.builder().token(token).build()

    setup_handlers(application)

    print("Bot starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    from telegram import Update
    run_bot()
