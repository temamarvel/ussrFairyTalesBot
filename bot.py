from telegram import ParseMode, ChatAction
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import boto3
import logging
import os
import psycopg2

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

session = boto3.session.Session()
s3 = session.client(
    service_name='s3',
    endpoint_url='https://storage.yandexcloud.net',
)

hello_text = 'Привет {}! \n\nЯ бот с аудиосказками и аудиоспектаклями. Пока я в стадии тестирования и умею не много. \n\nНапиши полное название сказки которую ищещь и я постараюсь найти ее для тебя.'


def hello(update, context):
    update.message.reply_text(hello_text.format(update.message.from_user.first_name))


def start(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,
                             text=hello_text.format(update.message.from_user.first_name))


def helpfunc(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,
                             text=hello_text.format(update.message.from_user.first_name))


def echo(update, context):
    context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.UPLOAD_AUDIO)

    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()

    # context.bot.send_message(chat_id=update.message.chat_id, text=update.message.text)

    # cursor.execute('SELECT surname FROM directors WHERE name = %s', (update.message.text,))
    # record = cursor.fetchone()
    # context.bot.send_message(chat_id=update.message.chat_id, text=update.message.text + " " + record[0])

    cursor.execute('SELECT title FROM tales WHERE title LIKE %%%s%%', (update.message.text,))
    record = cursor.fetchone()
    context.bot.send_message(chat_id=update.message.chat_id, text=update.message.text + " " + record[0])

    cover_name = update.message.text + '/' + 'cover.jpg'
    audio_name = update.message.text + '/' + update.message.text + '.mp3'

    photo_url = s3.generate_presigned_url("get_object", Params={"Bucket": "botdatabucket", "Key": cover_name.lower()},
                                          ExpiresIn=100)
    audio_url = s3.generate_presigned_url("get_object", Params={"Bucket": "botdatabucket", "Key": audio_name.lower()},
                                          ExpiresIn=100)

    # context.bot.send_message(chat_id=update.message.chat_id, text=audio_url)

    try:
        context.bot.send_photo(chat_id=update.message.chat_id,
                               photo=photo_url,
                               caption='[download audio](' + audio_url + ')',
                               parse_mode=ParseMode.MARKDOWN)
    except:
        context.bot.send_message(chat_id=update.message.chat_id, text='ничего не найдено')

    cursor.close()
    conn.close()


TOKEN = '668429632:AAHheR0-J4RfL1LYLOtX5nDTHfs4WJJrCWw'
PORT = int(os.environ.get('PORT', '8443'))

REQUEST_KWARGS = {
    'proxy_url': 'socks5://104.238.187.21:32245',
    # Optional, if you need authentication:
    #    'urllib3_proxy_kwargs': {
    #        'username': 'PROXY_USER',
    #        'password': 'PROXY_PASS',
    #  }
}

updater = Updater(token=TOKEN, use_context=True)


updater.dispatcher.add_handler(CommandHandler('hello', hello))
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('help', helpfunc))

updater.dispatcher.add_handler(MessageHandler(Filters.text, echo))

DATABASE_URL = os.environ['DATABASE_URL']


def custom(update, context):
    # cursor.execute('SELECT surname FROM directors WHERE name = %s', (update.message.text,))
    # record = cursor.fetchone()
    context.bot.send_message(chat_id=update.message.chat_id, text=update.message.text)


updater.dispatcher.add_handler(CommandHandler('custom', custom))

updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)
updater.bot.set_webhook("https://calm-shelf-64757.herokuapp.com/" + TOKEN)

# updater.start_polling()
updater.idle()
