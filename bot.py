from typing import Final
from telegram import Update, Bot
from telegram.ext import PollAnswerHandler
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, PollAnswerHandler
import pymongo

TOKEN: Final = '6943202093:AAH5ImfB-dGuxRQgjPtXJ6bj4Fhj8QdRaTE'
BOT_USERNAME: Final = '@carnegie_chat_bot'
uri: Final = 'mongodb+srv://carnegie_chat_bot:WelcomeBack@cybersphere.i4tnndd.mongodb.net/?retryWrites=true&w=majority&appName=Cybersphere'
commander_id: Final = 5380910790

responses_value_record = 0
myClient = pymongo.MongoClient(uri)
myDb = myClient["carnegie_chat_bot"]
myUser = myDb["users"]
myPermission = myDb["Permissions"]

#Command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Thanks for chatting with me. How may i help you?")
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("I am Carnegie Chat Bot (CCB), i am here to assist you with Carnegie's information!")
async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("This is a custom command!") 
async def permission_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global responses_value_record
    await update.message.reply_text("Are you asking for permission? To ask for permission please input the data such as: \n Your Name: \n Event:\n Date ")
    responses_value_record = 1
async def handle_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    poll_answer = update.poll_answer
    user_id = poll_answer.user.id
    option_ids = poll_answer.option_ids
    poll_id = poll_answer.poll_id

    permission_details = myPermission.find_one({"poll_id": poll_id})
    if permission_details:
        permission_statement = "Your permission for \n" + permission_details["details"] + "\n is "

        if 0 in option_ids:
            myPermission.update_one({"poll_id": poll_id}, {"$set": {"Approval": "Approved"}})
            await context.bot.send_message(permission_details["user_id"], permission_statement+"approved")
        elif 1 in option_ids:
            myPermission.update_one({"poll_id": poll_id}, {"$set": {"Approval": "Rejected"}})
            await context.bot.send_message(permission_details["user_id"], permission_statement+"rejected")
        else:
            myPermission.update_one({"poll_id": poll_id}, {"$set": {"Approval": "Resubmit"}})
            await context.bot.send_message(permission_details["user_id"], permission_statement+"not clear. Please resend a better version")

        print(f"User {user_id} answered with option IDs: {option_ids}")
    else:
        print(f"No permission details found for poll ID: {poll_id}")


#Responses
def separate_permission_info(text: str):
    rList = []
    myList = text.split("\n")
    for i in range(0, len(myList)):
        new_text: str = myList[int(i)]
        new_list = new_text.split(":")
        name = new_list[0]
        description = new_list[1]
        rList.append(name)
        rList.append(description)
    if len(rList) == 6:
        return rList
    else: 
        return False


def handle_responses(text: str):
    global user_id
    global user_info 
    global responses_value_record
    user_info = myUser.find_one({"user_id": str(user_id)})
    text = text.lower()
    if 'hello' in text:
        if user_info:
            return 'Hi ' + user_info["name"]
        else:
            return "Hey there"
    elif 'permissions' or 'permission' in text:
        responses_value_record = 1
        return "Are you asking for permission? To ask for permission please input the data such as: \n Your Name: \n Event:\n Date "
        
    
    return 'I do not understand what you wrote...'
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global user_id
    global responses_value_record
    global commander_id
    message_type = update.message.chat.type
    text = update.message.text
    user_id = update.message.chat_id
    print(f'User ({user_id}) in {message_type}: "{text}"')

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text = text.replace(BOT_USERNAME, "").strip()
            response = handle_responses(new_text)
        else:
            return
    else:
        if responses_value_record == 0:
            response = handle_responses(text)
        elif responses_value_record == 1:
            if separate_permission_info(text) == False:
                response = "Please input using the correct format :\n Name: <Your Name>\nEvent: <Event Name> "
            else:
                myList = separate_permission_info(text)
                question = "Permission\n" + text
                options = ["Approved", "Rejected", "Resubmit"]
                sent_poll = await context.bot.send_poll(chat_id=commander_id, question=question, options=options, is_anonymous=False)
                poll_id = sent_poll.poll.id  
                myPermission.insert_one({
                    "user_id": update.message.chat_id,
                    "poll_id": poll_id  ,
                    "details" : text,
                    str(myList[0]): str(myList[1]),
                    str(myList[2]): str(myList[3]),
                    str(myList[4]) : str(myList[5]),
                    "Approval": "",
                    "Time Sent": update.message.date
                })
                response = "Your responses have been recorded, Thankyou!"
                responses_value_record = 0

    
    print("Bot: ", response)
    await update.message.reply_text(response)
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

if __name__ == '__main__':
    print("Starting Bot...")
    app = Application.builder().token(TOKEN).build()
    poll_answer_handler = PollAnswerHandler(handle_poll_answer) 
    #Command
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))
    app.add_handler(CommandHandler('permission', permission_command))
    #Message
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    #Error
    app.add_error_handler(error)
    app.add_handler(PollAnswerHandler(handle_poll_answer))
    
    #polling
    print("Polling...")
    app.run_polling(poll_interval=1)
    