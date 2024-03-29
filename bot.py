from typing import Final
from telegram import Update, Bot
from telegram.ext import PollAnswerHandler
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, PollAnswerHandler
from dateutil import parser
from datetime import datetime, timedelta
import pymongo
import re


TOKEN: Final = '6943202093:AAH5ImfB-dGuxRQgjPtXJ6bj4Fhj8QdRaTE'
BOT_USERNAME: Final = '@carnegie_chat_bot'
uri: Final = 'mongodb+srv://carnegie_chat_bot:WelcomeBack@cybersphere.i4tnndd.mongodb.net/?retryWrites=true&w=majority&appName=Cybersphere'
commander_id: Final = 5380910790

myClient = pymongo.MongoClient(uri)
myDb = myClient["carnegie_chat_bot"]
myUser = myDb["users"]
myPermission = myDb["Permissions"]
myState = myDb["State"]

#Command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = myUser.find_one({"user_id": user_id})
    if s:
        await update.message.reply_text("Hello")
    else:
        set_state(3, user_id)
        await update.message.reply_text("Hello! Thanks for chatting with me. May i know some of your details?\n\nName: \nGender: \nStatus(P1 - SHS3 or Teacher): ")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("I am Carnegie Chat Bot (CCB), i am here to assist you with Carnegie's information!")
async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("This is a custom command!") 
async def permission_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    await update.message.reply_text("Are you asking for permission? To ask for permission please input the data such as: \n Your Name: \n Event:\n Date ")
    set_state(1, user_id)
async def handle_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    poll_answer = update.poll_answer
    user_id = poll_answer.user.id
    option_ids = poll_answer.option_ids
    poll_id = poll_answer.poll_id

    permission_details = myPermission.find_one({"poll_id": poll_id})
    if permission_details:
        permission_statement = "Your permission for \n" + permission_details["details"] + "\nis "

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
async def handle_reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    set_state(0, user_id)
#Responses
def extract_info(input_text: str):
    info = {"name": None, "date": None}

    # Convert input text to lowercase and remove any punctuation
    input_text = input_text.lower().strip()

    # Extract name and date using regular expressions
    name_match = re.search(r"name\s*:\s*(.*)", input_text)
    date_match = re.search(r"date\s*:\s*(.*)", input_text)


    # If name is found, extract it
    if name_match:
        info["name"] = name_match.group(1).strip()

    # If date is found, attempt to parse it
    if date_match:
        date_str = date_match.group(1).strip()
        if date_str.lower() == "today":
            info["date"] = datetime.now().strftime("%d %B %Y").lower()
        elif date_str.lower() == "tomorrow":
            tomorrow = datetime.now() + timedelta(days=1)
            info["date"] = tomorrow.strftime("%d %B %Y").lower()
        else:
            try:
                date_obj = parser.parse(date_str)
                info["date"] = date_obj.strftime("%d %B %Y").lower()
            except ValueError:
                pass  # Ignore if date parsing fails
    return info
def set_state(number: int, user_id):
    if myState.find_one({"user_id": user_id}):
        myState.update_one({"user_id": user_id}, {"$set": {"State": number}})
    else: 
        myState.insert_one({
            "user_id" : user_id,
            "State" : number
        })
def parse_date(input_date):
    try:
        parsed_date = parser.parse(input_date)
        standardized_date = parsed_date.strftime("%d %B %Y")
        return standardized_date
    except ValueError:
        return None
def separate_info(text: str, expectedLong: int, expectedData: str):
    rList = []
    myList = text.split("\n")
    if len(myList) != expectedLong:
        return False  # Return False if the format is incorrect

    for line in myList:
        parts = line.split(":")
        if len(parts) != 2:
            return False  # Return False if any line doesn't have exactly one colon
        if expectedData == "permission":
            name, description = parts[0].strip(), parts[1].strip()
            if name.lower() == "date" or name.lower() == "day":
                name = "date"
                if parse_date(description):
                    description = parse_date(description)
                else: 
                    return False
            rList.extend([name.lower(), description.lower()])
        elif expectedData == "new user":
            name, description = parts[0].strip(), parts[1].strip()
            if name.lower == "name" or name.lower() == "myname":
                name = "name"
            if "status" in name:
                name = "status"
            rList.extend([name.lower(), description.lower()])

    return rList
def handle_responses(text: str):
    global user_id
    global user_info 
    user_info = myUser.find_one({"user_id": str(user_id)})
    text = text.lower()
    if user_info:
        if 'hello' in text:
            return 'Hi ' + user_info["name"]
        elif 'permissions' in text or 'permission' in text:
            if 'access' in text:
                if myUser.find_one({"user_id": str(user_id)})["status"] == "teacher":
                    set_state(2, user_id)
                    return "Are you requesting for permission lists?\nPlease give me the permission info that you want to check\n\nStudent Name:\nDate:\n\nPut a hypen if there is no any requirement for the permission"
            else:
                set_state(1, user_id)
                return "Are you asking for permission? To ask for permission please input the data such as: \n\nEvent:\nDate: "
    else:
        set_state(3, user_id)
        return 'Hi, there seems that this is our first conversation. May i know your name and some of your details? \n\nName: \nGender: \nStatus(P1 - SHS3 or Teacher): '
    return 'I do not understand what you wrote...'
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global user_id
    global responses_value_record
    global commander_id
    message_type = update.message.chat.type
    text = update.message.text
    user_id = update.message.chat_id
    cr = myState.find_one({"user_id": user_id})

    print(f'User ({user_id}) in {message_type}: "{text}"')
    if cr:
        responses_value_record = cr["State"]
    else:
        responses_value_record = 0

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text = text.replace(BOT_USERNAME, "").strip()
            response = handle_responses(new_text)
    else:
        if responses_value_record == 0:
            response = handle_responses(text)
        elif responses_value_record == 1:
            myInfo = separate_info(text, 2, "permission")
            if myInfo == False:
                response = "Please input using the correct format :\n\nEvent: <Event Name>\nDate: <Event Date>"
            else:
                myList = myInfo
                question = "Permission\n" + myUser.find_one({"user_id": str(user_id)})['name'] +text
                options = ["Approved", "Rejected", "Resubmit"]
                sent_poll = await context.bot.send_poll(chat_id=commander_id, question=question, options=options, is_anonymous=False)
                poll_id = sent_poll.poll.id
                myPermission.insert_one({
                    "user_id": update.message.chat_id,
                    "poll_id": poll_id,
                    "details": text,
                    "name": myUser.find_one({"user_id": str(user_id)})['name'],
                    str(myList[0]): str(myList[1]),
                    str(myList[2]): str(myList[3]),
                    "Approval": "",
                    "Time Sent": update.message.date
                })
                response = "Your responses have been recorded, Thankyou!"
                myState.update_one({"user_id": user_id}, {"$set": {"State": 0}})
        elif responses_value_record == 2:
            new_list = extract_info(text)
            if new_list["name"] == None and new_list["date"] == None:
                response = "Please input the correct format!!!"
            else:
                if new_list["name"] != None and new_list["date"] != None:
                    query = {
                        "$or": [
                            {"name": new_list["name"]},
                            {"date": new_list["date"]}
                        ],
                        "Approval": "Approved"  # Add condition for approval status
                    }
                elif new_list["name"] == None and new_list["date"] != None:
                    print(new_list["date"])
                    query = {
                        "$or": [
                            {"date": new_list["date"]}
                        ],
                        "Approval": "Approved"  # Add condition for approval status
                    }
                elif new_list["name"] != None and new_list["date"] == None:
                    query = {
                        "$or": [
                            {"name": new_list["name"]}
                        ],
                        "Approval": "Approved"  # Add condition for approval status
                    }

                # Execute the query and retrieve the results
                results = myPermission.find(query)

                # Iterate over the cursor
                found = False
                response = "The Lists:\n\n"
                for result in results:
                    found = True
                    temp = result['name'] + "\n" + result['details'] + "\n=================================\n"
                    response += temp # Print only the 'details' field

                # If no results found, print a message
                if not found:
                    response = "There is no data that is suitable."
                set_state(0, user_id)
        elif responses_value_record == 3:
            myList = separate_info(text, 3, "new user")
            if myList:
                myUser.insert_one({
                        "user_id": str(update.message.chat_id),
                        str(myList[0]): str(myList[1]),
                        str(myList[2]): str(myList[3]),
                        str(myList[4]) : str(myList[5])
                    })
                response = "Thankyou, what can i do for you"
                set_state(0, user_id)
            else:
                response = "The format is not correct please fill as the correct format!"
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
    app.add_handler(CommandHandler('reset', handle_reset))
    #Message
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    #Error
    app.add_error_handler(error)
    app.add_handler(PollAnswerHandler(handle_poll_answer))
    
    #polling
    print("Polling...")
    app.run_polling(poll_interval=1)