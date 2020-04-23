from telegram.ext import (Updater , CommandHandler, MessageHandler, Filters, InlineQueryHandler,
                            CallbackQueryHandler, ConversationHandler)  #updater, dispatcher, handler
from telegram.error import (TelegramError, Unauthorized, BadRequest, 
                            TimedOut, ChatMigrated, NetworkError)
from telegram import (InlineQueryResultArticle, InputTextMessageContent, 
                            ReplyKeyboardMarkup, KeyboardButton , InlineKeyboardButton,
                            InlineKeyboardMarkup, ReplyKeyboardRemove) 
import logging 
from firestoredb import FirestoreDB
import os
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv('TELE_TOKEN')

#handle exception
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

logger= logging.getLogger(__name__)

ONE , TWO , THREE , FOUR , FIVE = range(5)

# rating_keyboard = [
#         [InlineKeyboardButton(1 , callback_data='1'), InlineKeyboardButton(2 , callback_data='2'),
#         InlineKeyboardButton(3 , callback_data='3'),InlineKeyboardButton(4 , callback_data='4'),
#         InlineKeyboardButton(5 , callback_data='5'),InlineKeyboardButton(6 , callback_data='6'),
#         InlineKeyboardButton(7 , callback_data='7'),InlineKeyboardButton(8 , callback_data='8'),
#         InlineKeyboardButton(9 , callback_data='9'),InlineKeyboardButton(10 , callback_data='10')]]


# where to put
db = FirestoreDB()
ques = db.get_item()
count = 0

def keyboards(count):
    rating_keyboard = [['1' , '2' , '3' , '4' , '5'],
                    ['6' , '7' , '8' , '9' , '10']]
    rating_markup = ReplyKeyboardMarkup(rating_keyboard , one_time_keyboard=True)
    remove_markup = ReplyKeyboardRemove()

    if(ques[count-1]['type']['rating'] == True):
        return rating_markup
    else:
        return remove_markup

def get_question(ind):
    global count
    count += 1
    return ques[ind]['question']

def start(update, context):
    reply_text ="{}".format(get_question(count))
    update.message.reply_text(reply_text, reply_markup=keyboards(count))

    return ONE

def prod_one(update, context):
    logger.info("input : %s ", update.message.text)
    reply_text ="{}".format(get_question(count))
    update.message.reply_text(reply_text , reply_markup= keyboards(count))
    return TWO

def prod_two(update, context):
    logger.info("input : %s ", update.message.text)  
    reply_text = "{}".format(get_question(count))
    update.message.reply_text(reply_text , reply_markup=keyboards(count))

    return THREE

def prod_three(update, context):
    logger.info("input %s ", update.message.text)  
    reply_text = "{}".format(get_question(count))
    update.message.reply_text(reply_text, reply_markup=keyboards(count))

    return FOUR

def prod_four(update, context):
    logger.info("input %s ", update.message.text)  
    reply_text = "DONE"
    update.message.reply_text(reply_text , reply_markup=keyboards(count))
    
    return ConversationHandler.END

def done(update, context):
    update.message.reply_text('Bye! Hope to hear form you again! /start to add more ')
    return ConversationHandler.END

def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Wrong Command! /start to get started")

# def msg_filter(count):
#     if(ques[count]['type']['closed_ended'] == True):
#         print('t')
#         return Filters.text
    
#     else:
#         print('r')
#         return Filters.regex('^(1|2|3|4|5|6|7|8|9|10)$')

def main():
    updater = Updater(token=TOKEN , use_context=True)
    dispatcher = updater.dispatcher
    print('before')
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start' , start)],

        states={
            ONE : [MessageHandler(Filters.text , prod_one)],

            TWO : [MessageHandler(Filters.regex('^(1|2|3|4|5|6|7|8|9|10)$') , prod_two)],

            THREE : [MessageHandler(Filters.regex('^(1|2|3|4|5|6|7|8|9|10)$') , prod_three)],

            FOUR : [MessageHandler(Filters.text , prod_four)],
        },
        fallbacks=[CommandHandler('done', done)],
        allow_reentry = True
    )
    print('done')
    dispatcher.add_handler(conversation_handler)

    #wrong command
    wrong_command = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(wrong_command)

    #start bot
    updater.start_polling() 

    #to send stop signal to the bot
    updater.idle() 

if __name__ == '__main__':
    main()
