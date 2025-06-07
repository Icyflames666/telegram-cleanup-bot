import telebot
import threading
import os
import time
from flask import Flask

# Initialize Flask app for Render port binding
app = Flask(_name_)
PORT = int(os.environ.get('PORT', 10000))

# Get Telegram bot token from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# Dictionary to track scheduled deletions {message_id: timer_object}
message_timers = {}

def schedule_delete(chat_id, message_id, delay=300):  # 300 seconds = 5 minutes
    """Schedule message deletion using threading Timer"""
    timer = threading.Timer(delay, delete_message, args=(chat_id, message_id))
    timer.start()
    # Store timer reference
    message_timers[message_id] = timer

def delete_message(chat_id, message_id):
    """Delete message and clean up timer reference"""
    try:
        bot.delete_message(chat_id, message_id)
    except Exception as e:
        print(f"Delete failed: {e}")
    finally:
        # Clean up timer reference
        if message_id in message_timers:
            del message_timers[message_id]

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    """Handle all incoming messages"""
    schedule_delete(message.chat.id, message.message_id)

def start_bot():
    """Start Telegram bot polling in background"""
    print("Starting Telegram bot...")
    bot.infinity_polling()

@app.route('/')
def home():
    """Health check endpoint for Render"""
    return "Telegram Cleanup Bot is running!"

if _name_ == '_main_':
    # Start bot in background thread
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Start Flask server on main thread
    print(f"Starting web server on port {PORT}...")
    app.run(host='0.0.0.0', port=PORT)
