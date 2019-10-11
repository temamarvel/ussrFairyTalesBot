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


def hello(update, context):
    update.message.reply_text('Привет {}'.format(update.message.from_user.first_name))





def start(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")


def echo(update, context):
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()
    context.bot.send_message(chat_id=update.message.chat_id, text=update.message.text)
    cursor.execute('SELECT surname FROM directors WHERE name = %s', (update.message.text,))
    record = cursor.fetchone()
    context.bot.send_message(chat_id=update.message.chat_id, text=update.message.text + " " + record[0])
    url = s3.generate_presigned_url("get_object", Params={"Bucket": "botdatabucket", "Key": "test_image.png"}, ExpiresIn=100)
    #context.bot.send_photo(chat_id=update.message.chat_id, photo='https://storage.yandexcloud.net/botdatabucket/test_image.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=07838786945a6d4db9a48879cd8ca10a75569b1eca9cc7c145fe6b22e50623cd&X-Amz-Date=20191011T062912Z&X-Amz-Credential=I89EjR7hpjWoYGE7xm7A%2F20191011%2Fus-east-1%2Fs3%2Faws4_request')
    context.bot.send_photo(chat_id=update.message.chat_id, photo=url)

    url = s3.generate_presigned_url("get_object", Params={"Bucket": "botdatabucket", "Key": "test_audio.mp3"}, ExpiresIn=100)
    #context.bot.send_audio(chat_id=update.message.chat_id, audio=url)
    context.bot.send_message(chat_id=update.message.chat_id, text='[download audio:](' + url + ')', parse_mode=telegram.ParseMode.MARKDOWN)

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

updater.dispatcher.add_handler(MessageHandler(Filters.text, echo))

DATABASE_URL = os.environ['DATABASE_URL']




def custom(update, context):
    #cursor.execute('SELECT surname FROM directors WHERE name = %s', (update.message.text,))
    #record = cursor.fetchone()
    context.bot.send_message(chat_id=update.message.chat_id, text=update.message.text)


updater.dispatcher.add_handler(CommandHandler('custom', custom))


updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)
updater.bot.set_webhook("https://calm-shelf-64757.herokuapp.com/" + TOKEN)

#updater.start_polling()
updater.idle()
