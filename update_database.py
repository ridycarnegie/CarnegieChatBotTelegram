from typing import Final
import pymongo

uri: Final = 'mongodb+srv://carnegie_chat_bot:WelcomeBack@cybersphere.i4tnndd.mongodb.net/?retryWrites=true&w=majority&appName=Cybersphere'

#Connecting Database
myClient = pymongo.MongoClient(uri)
myDb = myClient["carnegie_chat_bot"]
myCol = myDb["users"]

user_id = input("Insert your user id: ")
name = input("Insert your name: ")
gender = input("Insert your gender: ")
status = input("Input your status (which class or teacher): ")

myCol.insert_one({
    "user_id" : user_id,
    "name" : name,
    "gender": gender,
    "status": status
})
