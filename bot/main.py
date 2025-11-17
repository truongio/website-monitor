import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from dotenv import load_dotenv
from telegram.ext import Application
from .handlers import setup_handlers


load_dotenv()


def start_health_server():
    port = int(os.getenv("PORT", "0"))
    if port == 0:
        return None

    class HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"OK")

        def log_message(self, format, *args):
            return

    def serve():
        httpd = HTTPServer(("", port), HealthHandler)
        print(f"Health server listening on port {port}")
        httpd.serve_forever()

    thread = threading.Thread(target=serve, daemon=True)
    thread.start()
    return thread


def run_bot():
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")

    application = Application.builder().token(token).build()

    setup_handlers(application)

    start_health_server()
    print("Bot starting...")
    print("Bot started! Listening for updates. Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    from telegram import Update
    run_bot()
