from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import os
import psycopg2

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


def hello(update, context):
    update.message.reply_text('Hello {}'.format(update.message.from_user.first_name))


def custom(update, context):
    update.message.reply_text('Custom answer')
    #context.bot.send_photo(chat_id=update.message.chat_id, photo=open('images/414.png', 'rb'))


def start(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")


def echo(update, context):
    context.bot.send_message(chat_id=update.message.chat_id, text=update.message.text)


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

conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = conn.cursor()
cursor.execute('SELECT * FROM directors LIMIT 10')
record = cursor.fetchone()

updater.dispatcher.add_handler(CommandHandler(record, custom))

cursor.close()
conn.close()

updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)
updater.bot.set_webhook("https://calm-shelf-64757.herokuapp.com/" + TOKEN)

#updater.start_polling()
updater.idle()
