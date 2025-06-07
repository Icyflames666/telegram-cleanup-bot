import telebot
import threading
import os
from flask import Flask

app = Flask(_name_)

# SECURE: Get token ONLY from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable not set!")

# Additional security validation
if len(BOT_TOKEN) < 30 or ":" not in BOT_TOKEN:
    raise ValueError("Invalid bot token format!")

bot = telebot.TeleBot(BOT_TOKEN)

# Dictionary to track scheduled deletions
message_timers = {}

def schedule_delete(chat_id, message_id, delay=300):  # 5 minutes
    """Schedule message deletion using threading Timer"""
    def delete_wrapper():
        try:
            bot.delete_message(chat_id, message_id)
        except Exception as e:
            print(f"Delete failed: {e}")
        finally:
            if message_id in message_timers:
                del message_timers[message_id]
    
    timer = threading.Timer(delay, delete_wrapper)
    timer.start()
    message_timers[message_id] = timer

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    """Handle all incoming messages"""
    schedule_delete(message.chat.id, message.message_id)

def start_bot():
    """Start Telegram bot polling"""
    print("Starting Telegram bot polling...")
    bot.infinity_polling()

@app.route('/')
def health_check():
    """Health check endpoint for Render"""
    return "🟢 Telegram Auto-Clean Bot is Operational", 200

if _name_ == '_main_':
    # Start bot in background thread
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Start Flask server on main thread
    port = int(os.environ.get('PORT', 10000))
    print(f"Starting web server on port {port}...")
    app.run(host='0.0.0.0', port=port)
    
    # Start Flask server on main thread
    print(f"Starting web server on port {PORT}...")
    app.run(host='0.0.0.0', port=PORT)
