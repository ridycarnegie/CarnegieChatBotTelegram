import os
import logging
from uuid import uuid4

from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, ContextTypes, CommandHandler

TOKEN = os.environ.get('BOT_TOKEN')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

async def caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text_caps = ' '.join(context.args).upper()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

async def put(update, context):
    """Usage: /put value"""
    # Generate ID and separate value from command
    key = str(uuid4())
    key = context.args[0]
    # We don't use context.args here, because the value may contain whitespaces
    value = update.message.text.partition(' ')[2]
    value = value.partition(' ')[2]
    print(update.message.text)

    # Store value
    context.user_data[key] = value
    # Send the key to the user
    await update.message.reply_text(key)

async def get(update, context):
    """Usage: /get uuid"""
    # Separate ID from command
    key = context.args[0]

    # Load value and send it to the user
    value = context.user_data.get(key, 'Not found')
    await update.message.reply_text(value)

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler('start', start)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    caps_handler = CommandHandler('caps', caps)

    application.add_handler(start_handler)
    application.add_handler(echo_handler)
    application.add_handler(caps_handler)

    application.add_handler(CommandHandler('put', put))
    application.add_handler(CommandHandler('get', get))

    # default handler
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    application.add_handler(unknown_handler)

    application.run_polling()
