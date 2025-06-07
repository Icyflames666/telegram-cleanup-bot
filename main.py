import telebot
import threading
import os
import time
import requests
import logging
from flask import Flask

# Configure logging - FIXED
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(_name)  # FIXED: __name_ with double underscores

# Initialize Flask app - FIXED
app = Flask(_name)  # FIXED: __name_ with double underscores

# SECURE: Get token ONLY from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    logger.error("BOT_TOKEN environment variable not set!")
    raise RuntimeError("BOT_TOKEN environment variable not set!")

# Additional security validation
if len(BOT_TOKEN) < 30 or ":" not in BOT_TOKEN:
    logger.error("Invalid bot token format!")
    raise ValueError("Invalid bot token format!")

bot = telebot.TeleBot(BOT_TOKEN)
logger.info("Telegram bot initialized")

# Dictionary to track scheduled deletions
message_timers = {}

def schedule_delete(chat_id, message_id, delay=300):  # 5 minutes
    """Schedule message deletion using threading Timer"""
    def delete_wrapper():
        try:
            logger.info(f"Deleting message {message_id} in chat {chat_id}")
            bot.delete_message(chat_id, message_id)
        except Exception as e:
            logger.error(f"Delete failed: {e}")
        finally:
            if message_id in message_timers:
                del message_timers[message_id]
    
    timer = threading.Timer(delay, delete_wrapper)
    timer.start()
    message_timers[message_id] = timer
    logger.info(f"Scheduled deletion for message {message_id} in {delay} seconds")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    """Handle all incoming messages"""
    logger.info(f"New message: {message.message_id} in chat {message.chat.id}")
    schedule_delete(message.chat.id, message.message_id)

def start_bot():
    """Start Telegram bot polling"""
    logger.info("Starting Telegram bot polling...")
    bot.infinity_polling()

@app.route('/')
def health_check():
    """Health check endpoint for Render"""
    return "🟢 Telegram Auto-Clean Bot is Operational", 200

def keep_alive():
    """Prevent Render free tier from sleeping"""
    logger.info("Starting keep-alive thread")
    while True:
        try:
            # Get Render URL from environment variable
            render_url = os.getenv('RENDER_EXTERNAL_URL')
            if render_url:
                response = requests.get(render_url)
                logger.info(f"Keep-alive ping successful ({response.status_code})")
            else:
                logger.warning("Skipping keep-alive: RENDER_EXTERNAL_URL not set")
        except Exception as e:
            logger.error(f"Keep-alive failed: {e}")
        time.sleep(120)  # Ping every 2 minutes

if _name_ == '_main_':
    # Start bot in background thread
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Start keep-alive thread
    keep_alive_thread = threading.Thread(target=keep_alive)
    keep_alive_thread.daemon = True
    keep_alive_thread.start()
    
    # Start Flask server on main thread
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"Starting web server on port {port}...")
    app.run(host='0.0.0.0', port=port)
