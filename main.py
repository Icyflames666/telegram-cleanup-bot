import telebot
import threading
import os
import time
import requests
import logging
from flask import Flask

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(_name_)

# Initialize Flask app
app = Flask(_name_)

# Get bot token from environment
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("Missing BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)
logger.info("Bot initialized")

# Message tracking
message_timers = {}

def schedule_delete(chat_id, message_id, delay=300):
    def delete_wrapper():
        try:
            logger.info(f"Deleting {message_id}")
            bot.delete_message(chat_id, message_id)
        except Exception as e:
            logger.error(f"Delete failed: {e}")
        finally:
            if message_id in message_timers:
                del message_timers[message_id]
    
    timer = threading.Timer(delay, delete_wrapper)
    timer.start()
    message_timers[message_id] = timer
    logger.info(f"Scheduled deletion: {message_id}")

@bot.message_handler(func=lambda _: True)
def handle_message(message):
    logger.info(f"New message: {message.message_id}")
    schedule_delete(message.chat.id, message.message_id)

def start_bot():
    logger.info("Starting bot polling")
    bot.infinity_polling()

@app.route('/')
def health_check():
    return "🟢 Bot Running", 200

def keep_alive():
    logger.info("Keep-alive started")
    while True:
        try:
            if url := os.getenv('RENDER_EXTERNAL_URL'):
                requests.get(url)
                logger.info("Keep-alive ping sent")
        except Exception as e:
            logger.error(f"Ping failed: {e}")
        time.sleep(120)

if _name_ == '_main_':
    # Start bot thread
    threading.Thread(target=start_bot, daemon=True).start()
    
    # Start keep-alive thread
    threading.Thread(target=keep_alive, daemon=True).start()
    
    # Start web server
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port)
