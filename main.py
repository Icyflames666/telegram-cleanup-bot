import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def delete_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
    except Exception as e:
        print(f"Failed to delete message: {e}")

app = ApplicationBuilder().token(BOT_TOKEN).build()

# Match all types of messages
app.add_handler(MessageHandler(filters.ALL, delete_message))

if __name__ == "__main__":
    print("Bot is running...")
    app.run_polling()
