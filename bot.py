from telegram.ext import (Updater , CommandHandler, MessageHandler, Filters, InlineQueryHandler,
                            CallbackQueryHandler, ConversationHandler)  #updater, dispatcher, handler
# from telegram.error import (TelegramError, Unauthorized, BadRequest, TimedOut, ChatMigrated, NetworkError)
# from telegram import (InlineQueryResultArticle, InputTextMessageContent, ReplyKeyboardMarkup,
#                         KeyboardButton , InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove) 
import logging 
from db.firestoredb import FirestoreDB
from states.review_states import *
from states.info_states import *
from states.search import *
from states.start import *
from acessories.exception_log import *
from acessories.msg_filters import *

import os
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv('TELE_TOKEN')

# different constraints for bot status
START_OVER , REVIEW_DATA  , INFO_DATA , INFO_EXISTED  , REVIEW_QUESTION , INFO_QUESTION , PRODUCT_LIST ,NUM , ATTEMPT_COUNTER , INCENTIVE = range(10)
# constraints for bot states identification
SHOWING , SELECTING_OPTION ,END , DONE ,SEARCH , RECEIVEDATA , NEXT , INCENTIVE_COUNTER= range(8)
# global
db = FirestoreDB()
review_ques = db.get_question()
review_ques_id = db.get_question_id()
review_ques_dict = {}
user_ques = db.userinfo_question()
user_ques_id = db.userinfo_question_id()
user_ques_dict = {}

def done(update, context):
    update.message.reply_text('Bye! Hope to hear form you again! /start to add more ')
    return ConversationHandler.END

def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Wrong Command! /start to get started")

def new_end(update, context):
    print("val end")
    keyboard = [['NEXT']]
    markup = ReplyKeyboardMarkup(keyboard)
    reply_text = "Click next to the review question" 
    update.message.reply_text(reply_text , reply_markup=markup , one_time_keyboard=True)
    context.user_data[START_OVER] = False # after one conversation endede , reset constraint to false 

    return NEXT

def end(update, context):
    print('end')
    reply_text = "end . /start to start again" 
    update.message.reply_text(reply_text)
    return ConversationHandler.END

def main():
    ind = 0 
    updater = Updater(token=TOKEN , use_context=True)
    dispatcher = updater.dispatcher

    # update dictionary based on data (questions) in db
    # which will then used for the ConversationHandler's states
    for n in review_ques :
        review_ques_dict['STATES{}'.format(n+1)] = [MessageHandler(msg_filter(n+1, review_ques, review_ques_dict) , state(n+1 , review_ques , review_ques_id, user_ques , review_ques_dict , user_ques_dict, db))]
    for m in user_ques:
        user_ques_dict['INFO{}'.format(m+1)] = [MessageHandler(info_msg_filter(m+1 , user_ques, user_ques_dict) , user_info(m+1, review_ques , user_ques , user_ques_id, review_ques_dict ,user_ques_dict, db))]

    # third level conversation handler for product review 
    review_convo = ConversationHandler(
        entry_points=[MessageHandler(Filters.text('^NEXT$'), state(0, review_ques , review_ques_id, user_ques , review_ques_dict , user_ques_dict, db))], #start first question
        states = review_ques_dict,
        fallbacks=[MessageHandler(Filters.regex('^DONE$') , new_end),
                    CommandHandler('done' , end)],
        allow_reentry = True,
        map_to_parent={
            DONE : END
        })


    # second level conversation handler for product name validation 
    product_validation_convo = ConversationHandler(
        entry_points=[CommandHandler('review' , validate_product)],
        states ={ SEARCH : [MessageHandler(Filters.text , do_search)],
                    RECEIVEDATA : [MessageHandler(Filters.text('^No') , do_search),
                                MessageHandler(Filters.text('^Yes') , new_end)],
                    NEXT : [review_convo]
                },
        fallbacks=[MessageHandler(Filters.regex('^DONE$') , new_end),
                    CommandHandler('done' , end)],
        allow_reentry = True,
        map_to_parent={
            DONE : SEARCH
        })
        

    # second level conversation handler for user info 
    user_info_convo = ConversationHandler(
        entry_points=[CommandHandler('info' , user_info(0, review_ques , user_ques , user_ques_id, review_ques_dict ,user_ques_dict, db))],
        states = user_ques_dict,
        fallbacks=[MessageHandler(Filters.regex('^END$') , end),
                    CommandHandler('done' , end)],
        allow_reentry = True,
        map_to_parent={
            END : SHOWING 
        })
    
 
    #top level conversation handler
    top_level_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states ={
            SHOWING : [MessageHandler(Filters.regex('^END$') , start)],
            SELECTING_OPTION : [
                user_info_convo,
                product_validation_convo
            ]
        },
        fallbacks=[CommandHandler('done' , done)],
        allow_reentry = True)
    dispatcher.add_handler(top_level_handler)

    #wrong command
    wrong_command = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(wrong_command)

    #start bot
    updater.start_polling() 

    #to send stop signal to the bot
    updater.idle() 

if __name__ == '__main__':
    main()