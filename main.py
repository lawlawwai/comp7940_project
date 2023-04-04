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

    echo_photo_handler = MessageHandler(Filters.photo, echo_photo)
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', help_cmd))
    dispatcher.add_handler(CommandHandler(['photo', 'del_photo'], set_photo))
    dispatcher.add_handler(CommandHandler(['delete_match'], delete_match))

    updater.start_polling()
    updater.idle()


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Welcome to date bot!')
    # context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


def help_cmd(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Please fill below form to register.')
    update.message.reply_text('Name: \nAge: \nHeight: ')

def delete_match(update: Update, context: CallbackContext) -> None:
    user_id = str(update.effective_user.id)
    match_person_id = users_ref.child(user_id).child("Match").get()
    if match_person_id is None or match_person_id == "Waiting":
        update.message.reply_text("No match")
        return
    users_ref.child(user_id).child("Match").delete()
    users_ref.child(match_person_id).update({"Match": "Waiting"})
    update.message.reply_text("Deleted match")
    context.bot.send_message(chat_id=match_person_id, text="Match is deleted")


def set_photo(update: Update, context: CallbackContext) -> None:
    user_id = str(update.effective_user.id)
    user_ref = users_ref.child(user_id)
    if update.message.text == "/photo":
        user_ref.update({"Photo": "True"})
        update.message.reply_text("Send new photo to update")
    else:
        user_ref.update({"Photo": "False"})
        update.message.reply_text("Photo deleted")


def echo_photo(update: Update, context: CallbackContext) -> None:
    user_id = str(update.effective_user.id)
    user_ref = users_ref.child(user_id)
    photo_status = user_ref.child("Photo").get()
    input_photo = update.message.photo[1].file_id
    if photo_status == "True":
        user_ref.update({"Photo": input_photo})
        update.message.reply_text("Update photo")
    # context.bot.send_photo(chat_id=user_id, photo=input_photo)


if __name__ == '__main__':
    main()
