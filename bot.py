from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN: Final = '6943202093:AAH5ImfB-dGuxRQgjPtXJ6bj4Fhj8QdRaTE'
BOT_USERNAME: Final = '@carnegie_chat_bot'


#Command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Thanks for chatting with me. How may i help you?")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("I am Carnegie Chat Bot (CCB), i am here to assist you with Carnegie's information!")

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("This is a custom command!") 

#Responses
def handle_responses(text: str):
    text = text.lower()
    if 'hello' in text:
        return 'Hey there!'
    
    return 'I do not understand what you wrote...'


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type = update.message.chat.type
    text = update.message.text
    print(f'User ({update.message.chat_id}) in {message_type}: "{text}"')

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text = text.replace(BOT_USERNAME, "").strip()
            response = handle_responses(new_text)
        else:
            return
    else:
        response = handle_responses(text)
    
    print("Bot: ", response)
    await update.message.reply_text(response)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


if __name__ == '__main__':
    print("Starting Bot...")
    app = Application.builder().token(TOKEN).build()
    #Command
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))
    #Message
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    #Error
    app.add_error_handler(error)

    #polling
    print("Polling...")
    app.run_polling(poll_interval=1)