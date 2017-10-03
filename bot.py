from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import json
import os

from util import emodict_from_ogg, with_emoji, send_emo, emodict_from_wav, emo_distribution_text, logger
from accessories import actions, rev_actions, emoji_mapping, mapping, rev_mapping

####################
#  Here Goes Bot's #
#  Implementation  #
####################


def get_token():
    """
    Read bot's token from file
    :return: token
    """
    path = 'res/token_dev.json'

    with open(path) as jsn:
        data = json.load(jsn)
    return data['token']


def start(bot, update):
    """
    Propose to choose an action
    """
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
        emo_action = rev_actions[query.data]
        emotion = rev_mapping[emo_action]

        bot.edit_message_text(text="So you chose {emo}. Listen and record your own speech".format(emo=emo_action),
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)

        logger.info("Sent file: " + send_emo(emotion))
        bot.send_voice(chat_id=query.message.chat_id, voice=open(send_emo(emotion), 'rb'))

        # Send emotions by Tim Urban: https://www.ted.com/talks/tim_urban_inside_the_mind_of_a_master_procrastinator
        text = list()
        text.append(' --- Emotions by Tim Urban: ===> ')
        text.extend(emo_distribution_text(send_emo(emotion)))
        text.append(' <==== "Inside the mind of a master procrastinator" --- ')
        text = '\n'.join(text)

        query.message.reply_text(text)


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
    text.extend(emo_distribution_text(file_name_ogg))
    text.append(' <=======|----- ')
    text = '\n'.join(text)

    os.remove(file_name_ogg)
    os.remove(file_name_wav)

    update.message.reply_text(text)


def help_function(bot, update):
    update.message.reply_text('Help!')


def error(bot, update, error_arg):
    logger.warning('Update "%s" caused error "%s"' % (update, error_arg))


def echo(bot, update):
    update.message.reply_text("echo: " + update.message.text)


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
    logger.info("Hi!")
    main()
