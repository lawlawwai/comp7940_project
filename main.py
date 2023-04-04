import random
import re
import os
import telegram
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, CallbackContext
# The messageHandler is used for all message updates
import logging
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

## global DB setting
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://datebot-f12cb-default-rtdb.firebaseio.com/'
    # 'storageBucket': 'datebot-f12cb.appspot.com'
})
ref = db.reference('/')
users_ref = ref.child('users')


def main():
    # Load your token and create an Updater for your Bot
    TOKEN = os.getenv('BOTAPIKEY')
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    # You can set this logging module, so you will know when and why things do not work as e
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    # register a dispatcher to handle message: here we register an echo dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', help_cmd))
    dispatcher.add_handler(CommandHandler('myinfo', print_info))
    dispatcher.add_handler(CommandHandler(['print_random_user', 'print_match'], print_user))

    updater.start_polling()
    updater.idle()


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Welcome to date bot!')
    # context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


def help_cmd(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Please fill below form to register.')
    update.message.reply_text('Name: \nAge: \nHeight: ')
    
def print_info(update: Update, context: CallbackContext) -> None:
    user_id = str(update.effective_user.id)
    user_ref = users_ref.child(user_id)
    user_info = user_ref.get()
    if user_info is None:
        help_cmd(update, context)
        return
    reply_text = ""
    if "Photo" in user_info:
        if user_info["Photo"] != "True" and user_info["Photo"] != "False":
            context.bot.send_photo(chat_id=user_id, photo=user_info["Photo"])
    if "Name" in user_info:
        reply_text = reply_text + "Name: " + user_info["Name"] + "\n"
    if "Age" in user_info:
        reply_text = reply_text + "Age: " + user_info["Age"] + "\n"
    if "Height" in user_info:
        reply_text = reply_text + "Height: " + user_info["Height"] + "\n"
    if "Gender" in user_info:
        reply_text = reply_text + "Gender: " + user_info["Gender"] + "\n"
    update.message.reply_text(reply_text)


def print_user(update: Update, context: CallbackContext) -> None:
    input_command = update.message.text
    user_id = str(update.effective_user.id)
    if users_ref.child(user_id).get() is None:
        help_cmd(update, context)
        return
    if input_command == '/print_random_user':
        snapshot = users_ref.order_by_key().get()
        if len(list(snapshot.items())) <= 1:
            update.message.reply_text("End of list")
            return

        user_check = random.randint(0, len(list(snapshot.items())) - 1)
        user_check_result = list(snapshot.items())[user_check]
        while user_check_result[0] == user_id:
            user_check = random.randint(0, len(list(snapshot.items())) - 1)
            user_check_result = list(snapshot.items())[user_check]
    else:
        match_person_id = users_ref.child(user_id).child("Match").get()
        if match_person_id is None or match_person_id == "Waiting":
            update.message.reply_text("No match.")
            return
        user_check_result = list(users_ref.order_by_key().equal_to(match_person_id).get().items())[0]

    reply_text = "User info:\n"
    if "Photo" in user_check_result[1]:
        if user_check_result[1]["Photo"] != "True" and user_check_result[1]["Photo"] != "False":
            context.bot.send_photo(chat_id=user_id, photo=user_check_result[1]["Photo"])
    if "Name" in user_check_result[1]:
        reply_text = reply_text + "Name: " + user_check_result[1]["Name"] + "\n"
    if "Age" in user_check_result[1]:
        reply_text = reply_text + "Age: " + user_check_result[1]["Age"] + "\n"
    if "Height" in user_check_result[1]:
        reply_text = reply_text + "Height: " + user_check_result[1]["Height"] + "\n"
    if "Gender" in user_check_result[1]:
        reply_text = reply_text + "Gender: " + user_check_result[1]["Gender"] + "\n"
    update.message.reply_text(reply_text)


if __name__ == '__main__':
    main()
