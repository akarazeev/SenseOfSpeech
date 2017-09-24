from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from enum import Enum
import logging
import emoji
import json
import sys
import os

from util import emotion_wrapper, with_emoji

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

#############
#  Actions  #
#############

actions = {
    'DETECT': '1',
    'TRAIN': '2',
    'Fear': '3',
    'Happy': '4'
}

rev_actions = dict(zip(actions.values(), actions.keys()))

####################
#  Here Goes Bot's #
#  Implementation  #
####################

def get_token():
    path = 'token.json'
    with open(path) as jsn:
        data = json.load(jsn)
    return data['token']


def start(bot, update):
    update.message.reply_text('Hi!')
    keyboard = [[InlineKeyboardButton("Detect Emotions", callback_data=actions['DETECT']),
                 InlineKeyboardButton("Train Emotions", callback_data=actions['TRAIN'])]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Please choose:', reply_markup=reply_markup)


def button(bot, update):
    query = update.callback_query

    if query.data == actions['DETECT']:
        bot.edit_message_text(text="Let's detect emotions. Please, send me an audio message",
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
    elif query.data == actions['TRAIN']:
        bot.edit_message_text(text="Let's train emotions",
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)

        keyboard = [[InlineKeyboardButton("Fear", callback_data=actions['Fear']),
                     InlineKeyboardButton("Happy", callback_data=actions['Happy'])]]

        reply_markup = InlineKeyboardMarkup(keyboard)
        query.message.reply_text('Please choose emotion:', reply_markup=reply_markup)
    else:
        bot.edit_message_text(text="So you chose {emo}".format(emo=rev_actions[query.data]),
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)



def help_function(bot, update):
    update.message.reply_text('Help!')


def error(bot, update, error_arg):
    logger.warning('Update "%s" caused error "%s"' % (update, error_arg))


def echo(bot, update):
    update.message.reply_text("echo: " + update.message.text)


def emotion_handler(bot, update):
    """
    :param bot:
    :param update:
    :return:
    """
    file_id = update.message.voice.file_id
    file = bot.getFile(file_id)

    # Download file
    file_name_ogg = file_id + ".ogg"
    file_name_wav = file_id + ".wav"
    file.download(file_name_ogg)

    emo_mapping = {
        'anger': ':astonished:',
        'fear': ':scream:',
        'happiness': ':smile:',
        'neutrality': ':neutral_face:',
        'sadness': ':pensive:'
    }

    text = []

    text.append(' -----|=======> ')
    # file_name_ogg = 'wow_sure.ogg'
    valid, emo_dict = emotion_wrapper(file_name_ogg)

    if valid:
        text.extend(with_emoji(emo_dict, emo_mapping))
    else:
        err_message = "(-_-)"
        text.append(err_message)
    text.append(' <=======|----- ')

    text = '\n'.join(text)

    os.remove(file_name_ogg)
    os.remove(file_name_wav)

    update.message.reply_text(text)


def main():
    updater = Updater(get_token())
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_function))
    dp.add_error_handler(error)

    # on noncommand i.e message
    dp.add_handler(MessageHandler(Filters.text, echo))
    # dp.add_handler(MessageHandler(Filters.text, emotion_handler))

    # on voice messages - reply with emotions
    dp.add_handler(MessageHandler(Filters.voice, emotion_handler))
    dp.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    print("-> Hi!")
    main()
