from telegram.ext import (Updater , CommandHandler, MessageHandler, Filters, InlineQueryHandler,
                            CallbackQueryHandler, ConversationHandler)  #updater, dispatcher, handler
from telegram.error import (TelegramError, Unauthorized, BadRequest, TimedOut, ChatMigrated, NetworkError)
from telegram import (InlineQueryResultArticle, InputTextMessageContent, ReplyKeyboardMarkup,
                        KeyboardButton , InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove) 
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

SELECTING_OPTION , END , SHOWING = range(3)

# global
db = FirestoreDB()
ques = db.get_question()
ques_id = db.get_question_id()
states_dict = {}
user_ques = db.userinfo_question()
user_ques_id = db.userinfo_question_id()
user_ques_dict = {}

# return the correct type of keyboard for each type of questions
def keyboards(count):
    rating_keyboard = [['1' , '2' , '3' , '4' , '5'],
                    ['6' , '7' , '8' , '9' , '10']]
    rating_markup = ReplyKeyboardMarkup(rating_keyboard , one_time_keyboard=True)
    end_keyboard = ['Yes' , 'No']
    end_markup = ReplyKeyboardMarkup(end_keyboard , one_time_keyboard=True)

    remove_markup = ReplyKeyboardRemove()
    if(count < len(states_dict)):
        if(ques[count]['type'] == 'rating'):
            return rating_markup 
        else:
            return remove_markup

#return question id
def get_question_id(count):
    return ques_id[count]

# return question
def get_question(count):
    return ques[count]['question']

# return question
def get_userinfo_question(count):
    return user_ques[count]['question']

def get_userinfo_question_id(count):
    return user_ques_id[count]

def done(update, context):
    update.message.reply_text('Bye! Hope to hear form you again! /start to add more ')
    return ConversationHandler.END

def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Wrong Command! /start to get started")

# return the correct filters for MessageHandler 
def msg_filter(count):
    if(count <= len(states_dict)):
        if(ques[count]['type'] == 'open_ended'):
            return Filters.text
        else:
            return Filters.regex('^(1|2|3|4|5|6|7|8|9|10)$')

def info_msg_filter(count):
    if(count <= len(user_ques_dict)):
        if(user_ques[count]['type'] == 'open_ended'):
            return Filters.text
        else:
            return Filters.regex('^(1|2|3|4|5|6|7|8|9|10)$')


def into_list(user_data):
    data_list = list()

    for key, value in user_data.items():
        data_list.append('{} - {}'.format(key, value))

    return "\n".join(data_list).join(['\n', '\n'])

def question_info_list(user_data):
    data_list = list()

    for key, value in user_data.items():
        data_list.append('{} - {}'.format(key, value))

    return "\n".join(data_list).join(['\n', '\n'])

# callback function for MessageHandler in ConversationHandler
def state(count):
    def _state(update, context):
        text = update.message.text
        user_id = update.message.from_user.id
        logger.info("input %s ", text)
        user_data = context.user_data

        #add data to memory in user_data dictionary
        if(count != 0 ):        
            key = get_question_id(count-1)
            user_data[key] = text
            into_list(user_data)

        # check if the count doesnt exceed the state's dict length
        # when it reaches the last state's dict, the conversation will end
        if(count == len(states_dict)):
            reply_text = "This is the review details you have give us. See you again!. {}".format(into_list(user_data))
            update.message.reply_text(reply_text, reply_markup=ReplyKeyboardRemove())
            db.insert_item(user_id, user_data) #insert to db
            return ConversationHandler.END
        else:
            reply_text = "{}".format(get_question(count))
            update.message.reply_text(reply_text, reply_markup=keyboards(count))
            return 'STATES{}'.format(count + 1)

    return _state

def user_info(count_info):
    def _user_info(update, context):
        keyboard = [['END']]
        markup = ReplyKeyboardMarkup(keyboard)

        # check if the count doesnt exceed the state's dict length
        # when it reaches the last state's dict, the conversation will end
        if(count_info == len(user_ques_dict)):
            reply_text = "Thanks! We have got your information.")
            update.message.reply_text(reply_text, reply_markup=markup)
            # db.insert_item(user_id, user_data) #insert to db
            # user_data.clear()
            return END
        else:
            reply_text = "{}".format(get_userinfo_question(count_info))
            update.message.reply_text(reply_text, reply_markup=keyboards(count_info))
            return 'INFO{}'.format(count_info + 1)

    return _user_info

def start(update, context):
    rating_keyboard = [['Info'],['Review']]
    rating_markup = ReplyKeyboardMarkup(rating_keyboard , one_time_keyboard=True)
    update.message.reply_text("Welcome!" , reply_markup=rating_markup)

    return SELECTING_OPTION 

def end(update, context):
    print('DONE')

def main():
    updater = Updater(token=TOKEN , use_context=True)
    dispatcher = updater.dispatcher

    # update dictionary based on data (questions) in db
    # which will then used for the ConversationHandler's states
    for n in ques :
        states_dict['STATES{}'.format(n+1)] = [MessageHandler(msg_filter(n+1) , state(n+1))]

    for m in user_ques:
        user_ques_dict['INFO{}'.format(m+1)] = [MessageHandler(info_msg_filter(m+1) , user_info(m+1))]

    # second level conversation handler for user info 
    user_info_convo = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('^(Info)$') , user_info(0))],
        states = user_ques_dict,
        fallbacks=[MessageHandler(Filters.regex('^END$') , end)],
        allow_reentry = True,
        map_to_parent={
            END : SHOWING 
        })
    
    # second level conversation handler for user review
    review_convo = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('^Review$') , state(0))],
        states = states_dict,
        fallbacks=[CommandHandler('done', done)],
        allow_reentry = True)

    #top level conversation handler
    top_level_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states ={
            SHOWING : [MessageHandler(Filters.regex('^END$') , start)],
            SELECTING_OPTION : [
                user_info_convo,
                review_convo
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
