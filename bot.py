from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import logging
import json
import os

from util import emotion_wrapper, with_emoji, send_emo, emodict_from_path, OS

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

#############
#  Actions  #
#############

actions = {
    'DETECT':  '1',
    'TRAIN':   '2',
    'Neutral': '3',
    'Happy':   '4',
    'Sad':     '5',
    'Excited': '6',
    'Fear':    '7'
}

rev_actions = dict(zip(actions.values(), actions.keys()))

emo_mapping = {
    'anger':      ':astonished:',
    'fear':       ':scream:',
    'happiness':  ':smile:',
    'neutrality': ':neutral_face:',
    'sadness':    ':pensive:'
}

mapping = {
    'anger':      'Excited',
    'fear':       'Fear',
    'happiness':  'Happy',
    'neutrality': 'Neutral',
    'sadness':    'Sad'
}

####################
#  Here Goes Bot's #
#  Implementation  #
####################


def get_token():
    if OS == 'mac':
        path = 'res/token_finn.json'
    elif OS == 'linux':
        path = 'res/token_sos.json'
    with open(path) as jsn:
        data = json.load(jsn)
    return data['token']


def start(bot, update):
    update.message.reply_text('Hi!')
    keyboard = [[InlineKeyboardButton("Detect Emotions", callback_data=actions['DETECT']),
                 InlineKeyboardButton("Train Emotions",  callback_data=actions['TRAIN'])]]

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
        keyboard = [[InlineKeyboardButton("Neutral", callback_data=actions['Neutral']),
                     InlineKeyboardButton("Happy",   callback_data=actions['Happy']),
                     InlineKeyboardButton("Sad",     callback_data=actions['Sad']),
                     InlineKeyboardButton("Excited", callback_data=actions['Excited']),
                     InlineKeyboardButton("Fear",    callback_data=actions['Fear'])]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.message.reply_text('Please choose emotion:', reply_markup=reply_markup)
    else:
        rev_mapping= dict(zip(mapping.values(), mapping.keys()))

        emo_action = rev_actions[query.data]
        emotion = rev_mapping[emo_action]

        bot.edit_message_text(text="So you chose {emo}. Listen and record your own speech".format(emo=emo_action),
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)

        print('-> ' + send_emo(emotion))
        bot.send_voice(chat_id=query.message.chat_id, voice=open(send_emo(emotion), 'rb'))

        # Send emotions by Tim Urban: https://www.ted.com/talks/tim_urban_inside_the_mind_of_a_master_procrastinator
        text = list()

        text.append(' --- Emotions by Tim Urban: ===> ')
        valid, emo_dict = emodict_from_path(send_emo(emotion))

        if valid:
            text.extend(with_emoji(emo_dict, emo_mapping))
        else:
            err_message = "\_(^_^)_/"
            text.append(err_message)
        text.append(' <==== "Inside the mind of a master procrastinator" --- ')

        text = '\n'.join(text)

        query.message.reply_text(text)


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

    text = list()

    text.append(' -----|=======> ')
    valid, emo_dict = emotion_wrapper(file_name_ogg)

    if valid:
        text.extend(with_emoji(emo_dict, emo_mapping))
    else:
        err_message = "\_(^_^)_/"
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

    # on non-command messages
    dp.add_handler(MessageHandler(Filters.text, echo))

    # on voice messages - reply with emotions
    dp.add_handler(MessageHandler(Filters.voice, emotion_handler))
    dp.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    print("-> Hi!")
    main()
