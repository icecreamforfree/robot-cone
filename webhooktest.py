from telegram.ext import (Updater , CommandHandler, MessageHandler, Filters, InlineQueryHandler,
                            CallbackQueryHandler, ConversationHandler)  #updater, dispatcher, handler
import telegram
from flask import Flask, request, Response
from acessories.exception_log import *
import os
import json
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv('TELE_TOKEN')
HOST = os.getenv('SERVER_HOST')
SSL_CERT = './secrets/keys/ssl_cert.pem'  # Path to the ssl certificate
SSL_PRIV = './secrets/keys/pkey.pem'  # Path to the ssl private key
CERT = './secrets/keys/cert.pem'  # Path to the ssl private key

PORT = 8443

server = Flask(__name__)
bot = telegram.Bot(token=TOKEN)

def start(update, context):
    print('start')
    reply_text = "Welcome welcome welcome \n /review to start giving review \n /info to add info about yourself"
    # rating_markup = ReplyKeyboardMarkup(rating_keyboard , one_time_keyboard=True)
    update.message.reply_text(reply_text)


def main():
    updater = Updater(token=TOKEN , use_context=True)
    dispatcher = updater.dispatcher
    # Set webhook
    dispatcher.add_handler(CommandHandler('start', start, pass_args=True))
    # print(bot.getMe())
    try:
        updater.start_webhook(listen='127.0.0.1', port=5000, url_path=TOKEN)
        # updater.bot.set_webhook(url='https://{HOST}/{TOKEN}'.format(HOST=HOST, TOKEN=TOKEN), certificate=open(SSL_CERT, 'rb'))
        # updater.start_webhook(listen='0.0.0.0',
        #                 port=8443,
        #                 url_path=TOKEN,
        #                 key=SSL_PRIV,
        #                 cert=SSL_CERT,
        #                 webhook_url='https://{URL}:{PORT}/{TOKEN}'.format(URL=HOST, PORT=PORT, TOKEN=TOKEN))
        # return Response('Ok', status=200)

        print('in')
    except:
        print('failed')

# main()

# @server.route('/{}'.format(TOKEN)  , methods=['POST'])
# def respond():
#     if request.method == 'POST':
#         # retrieve the message in JSON and then transform it to Telegram object
#         update = telegram.Update.de_json(request.get_json(force=True), bot)
#         bot.process_new_updates([telegram.Update.de_json(request.stream.read().decode("utf-8"))])
#         chat_id = update.message.chat.id
#         msg_id = update.message.message_id

#         # # Telegram understands UTF-8, so encode text for unicode compatibility
#         text = update.message.text.encode('utf-8').decode()
#         print("got text message " , text)
#         return 'ok'
#     else:
#         return redirect("https://telegram.me/links_forward_bot", code=302)
#     response = "hi"
#     bot.sendMessage(chat_id=chat_id, text=response, reply_to_message_id=msg_id)

    

# @server.route('/setWebhook', methods=['GET', 'POST'])
# def set_webhook():
#     s = bot.set_webhook('https://{0}/'.format(HOST) + TOKEN)
#     if s:
#         return 'webhook ok'
#     else:
#         return 'webhook not ok'
# # # main()
# @server.route('/' , methods=['POST', 'GET'])
# def index():
#     print('get')
#     return '<h1>Webhook</h1>'
#     # return Response('Ok', status=200)


if __name__ == '__main__':
    main()
    # server.run(debug=True, threaded=True)
