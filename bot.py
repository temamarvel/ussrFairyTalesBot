from telegram import ParseMode, ChatAction
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import boto3
import logging
import os
import psycopg2

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

DATABASE_URL = os.environ['DATABASE_URL']
TOKEN = '668429632:AAHheR0-J4RfL1LYLOtX5nDTHfs4WJJrCWw'
PORT = int(os.environ.get('PORT', '8443'))
HEROKU_APP = 'https://calm-shelf-64757.herokuapp.com/'
BUCKET_NAME = 'botdatabucket'
COVER_IMAGE_NAME = 'cover.jpg'

session = boto3.session.Session()
s3 = session.client(
    service_name='s3',
    endpoint_url='https://storage.yandexcloud.net',
)

hello_text = 'Привет {}! ' \
             '\n\nЯ бот с аудиосказками и аудиоспектаклями. Пока я в стадии тестирования и умею не много. ' \
             '\n\nНапиши полное название сказки которую ищещь и я постараюсь найти ее для тебя.'


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

    sql_query = 'SELECT title FROM tales WHERE title LIKE %s'
    search_text = ['%' + update.message.text + '%']

    cursor.execute(sql_query, search_text)
    records = cursor.fetchall()

    for record in records:
        get_audio_from_cloud(context, update, record)

    cursor.close()
    conn.close()


def get_audio_from_cloud(context, update, record):
    title = record[0]
    context.bot.send_message(chat_id=update.message.chat_id, text=title)

    cover_name = title + '/' + COVER_IMAGE_NAME
    audio_name = title + '/' + title + '.mp3'
    photo_url = s3.generate_presigned_url("get_object",
                                          Params={"Bucket": BUCKET_NAME, "Key": cover_name.lower()},
                                          ExpiresIn=100)
    audio_url = s3.generate_presigned_url("get_object",
                                          Params={"Bucket": BUCKET_NAME, "Key": audio_name.lower()},
                                          ExpiresIn=100)

    try:
        context.bot.send_photo(chat_id=update.message.chat_id,
                               photo=photo_url,
                               caption='[download audio](' + audio_url + ')',
                               parse_mode=ParseMode.MARKDOWN)
    except:
        context.bot.send_message(chat_id=update.message.chat_id, text='ничего не найдено')


updater = Updater(token=TOKEN, use_context=True)

updater.dispatcher.add_handler(CommandHandler('hello', hello))
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('help', helpfunc))
updater.dispatcher.add_handler(MessageHandler(Filters.text, echo))

updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)
updater.bot.set_webhook(HEROKU_APP + TOKEN)

updater.idle()
