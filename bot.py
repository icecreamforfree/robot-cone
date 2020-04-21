from telegram.ext import (Updater , CommandHandler, MessageHandler, Filters, InlineQueryHandler,
                            CallbackQueryHandler, ConversationHandler)  #updater, dispatcher, handler
from telegram.error import (TelegramError, Unauthorized, BadRequest, 
                            TimedOut, ChatMigrated, NetworkError)
from telegram import (InlineQueryResultArticle, InputTextMessageContent, 
                            ReplyKeyboardMarkup, KeyboardButton , InlineKeyboardButton,
                            InlineKeyboardMarkup, ReplyKeyboardRemove) 
import logging 
import os
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv('TELE_TOKEN')

#handle exception
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

logger= logging.getLogger(__name__)

NAME , RATING , REPURCHASE , RECOMMEND , CHOOSING = range(5)

# rating_keyboard = [
#         [InlineKeyboardButton(1 , callback_data='1'), InlineKeyboardButton(2 , callback_data='2'),
#         InlineKeyboardButton(3 , callback_data='3'),InlineKeyboardButton(4 , callback_data='4'),
#         InlineKeyboardButton(5 , callback_data='5'),InlineKeyboardButton(6 , callback_data='6'),
#         InlineKeyboardButton(7 , callback_data='7'),InlineKeyboardButton(8 , callback_data='8'),
#         InlineKeyboardButton(9 , callback_data='9'),InlineKeyboardButton(10 , callback_data='10')]]
rating_keyboard = [['1' , '2' , '3' , '4' , '5'],
                    ['6' , '7' , '8' , '9' , '10']]
rating_markup = ReplyKeyboardMarkup(rating_keyboard , one_time_keyboard=True)

choosing_keyboard = [['Yes'] , ['No']]                    
choosing_markup = ReplyKeyboardMarkup(choosing_keyboard , one_time_keyboard=True)

def start(update, context):
    reply_text ='Hi! This is a customer review bot. Lets start! ' \
                'What is the name of the product?'
    update.message.reply_text(reply_text)

    return NAME

def prod_name(update, context):
    logger.info("product name is : %s ", update.message.text)
    update.message.reply_text("I see! How much would u like to rate this product",
                                reply_markup= rating_markup)

    return RATING

def prod_rating(update, context):
    logger.info("product rating is : %s ", update.message.text)  
    reply_text = "Received the ratings {}. " \
                "Next , how likely are you going to repeat your purchase?" \
                .format(update.message.text)
    update.message.reply_text(reply_text, reply_markup=rating_markup)

    return REPURCHASE

def prod_repurchase(update, context):
    logger.info("repurchase again rating is : %s ", update.message.text)  
    reply_text = "Yay! cant wait to see you again! " \
                "What product or service do you wish we carried?"
    update.message.reply_text(reply_text)

    return RECOMMEND

def prod_recommend(update, context):
    logger.info("recommended product is : %s ", update.message.text)  
    reply_text = "We will take {} into consideration. " \
                "You will hear some good news from us! " \
                "If you would like to review another product press /start" \
                .format(update.message.text)
    update.message.reply_text(reply_text , reply_markup=choosing_markup)

    return CHOOSING

def done(update, context):
    update.message.reply_text('BYE')
    return ConversationHandler.END

def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Wrong Command! /start to get started")

def main():

    updater = Updater(token=TOKEN , use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start' , start)],

        states={
            NAME : [MessageHandler(Filters.text , prod_name)],

            RATING : [MessageHandler(Filters.regex('^(1|2|3|4|5|6|7|8|9|10)$'), prod_rating)],

            REPURCHASE : [MessageHandler(Filters.regex('^(1|2|3|4|5|6|7|8|9|10)$'), prod_repurchase)],

            RECOMMEND : [MessageHandler(Filters.text, prod_recommend)],

            CHOOSING : [MessageHandler(Filters.regex('^Yes$'), start),
                        MessageHandler(Filters.regex('^No$'), done)]
            
        },
        fallbacks=[CommandHandler('done', done)],

        allow_reentry=True
    )

    dispatcher.add_handler(conv_handler)

    #wrong command
    wrong_command = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(wrong_command)

    #start bot
    updater.start_polling() 

    #to send stop signal to the bot
    updater.idle() 

if __name__ == '__main__':
    main()


