import telebot
import threading
import os

# Your Telegram bot token
BOT_TOKEN = os.getenv("BOT_TOKEN") or "7811300162:AAEAE82ML6q1GI45SzqNtrKzJw9Fv4Xn2kA"

bot = telebot.TeleBot(BOT_TOKEN)

# Function to schedule deletion
def schedule_delete(chat_id, message_id, delay=900):  # 900 seconds = 15 minutes
    threading.Timer(delay, lambda: delete_message(chat_id, message_id)).start()

def delete_message(chat_id, message_id):
    try:
        bot.delete_message(chat_id, message_id)
    except Exception as e:
        print(f"Failed to delete message: {e}")

# Handle all messages in the group
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    schedule_delete(message.chat.id, message.message_id)

bot.polling(non_stop=True)
