from typing import Final
from telegram import Update, Bot
from telegram.ext import PollAnswerHandler
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, PollAnswerHandler
from dateutil import parser
from datetime import datetime, timedelta
import pymongo
import re
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Define the function to start the form
def start(update: Update, context: te):
    reply_keyboard = [['Name', 'Age'], ['Email', 'Done']]
    update.message.reply_text(
        'Hi! Please fill out this form:',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )

# Define a function to handle user input
def handle_text(update, context):
    text = update.message.text
    user_input = context.user_data.setdefault('input', {})  # Store user input in user_data
    user_input[text] = update.message.from_user.id

# Define a function to end the form
def end(update, context):
    user_input = context.user_data.get('input', {})
    update.message.reply_text(f'Thank you! Here\'s what you submitted:\n{user_input}')
    context.user_data.clear()  # Clear user data for next form

# Set up the bot
def main():
    updater = Updater("6943202093:AAH5ImfB-dGuxRQgjPtXJ6bj4Fhj8QdRaTE", use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))
    dp.add_handler(MessageHandler(Filters.regex('^Done$'), end))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()