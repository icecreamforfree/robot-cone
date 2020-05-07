from telegram.ext import (Updater , CommandHandler, MessageHandler, Filters, InlineQueryHandler,
                            CallbackQueryHandler, ConversationHandler)  #updater, dispatcher, handler
from telegram.error import (TelegramError, Unauthorized, BadRequest, TimedOut, ChatMigrated, NetworkError)
from telegram import (InlineQueryResultArticle, InputTextMessageContent, ReplyKeyboardMarkup,
                        KeyboardButton , InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove) 
import logging 
from firestoredb import FirestoreDB
from geopy.geocoders import Nominatim
from text_search import search_text
import os
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv('TELE_TOKEN')

#geocoding
geolocator = Nominatim(user_agent="icecreamforfree")

#handle exception
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

logger= logging.getLogger(__name__)

SELECTING_OPTION , END , SHOWING , VALIDATE , REVIEW , DONE , SECOND_SHOWING , SEARCH , RECEIVEDATA , NEXT= range(10)

# global
db = FirestoreDB()
ques = db.get_question()
ques_id = db.get_question_id()
states_dict = {}
user_ques = db.userinfo_question()
user_ques_id = db.userinfo_question_id()
user_ques_dict = {}

# return the correct type of keyboard for each type of questions
def keyboards(count, iden):
    rating_keyboard = [['1' , '2' , '3' , '4' , '5'],
                    ['6' , '7' , '8' , '9' , '10']]
    rating_markup = ReplyKeyboardMarkup(rating_keyboard , one_time_keyboard=True)
    end_keyboard = ['Yes' , 'No']
    end_markup = ReplyKeyboardMarkup(end_keyboard , one_time_keyboard=True)
    remove_markup = ReplyKeyboardRemove()
    location_keyboard = [[KeyboardButton(text="send_location", request_location=True)]]
    location_markup = ReplyKeyboardMarkup(location_keyboard)
    if(iden == 'review'):
        if(count < len(states_dict)):
            if(ques[count]['type'] == 'rating'):
                return rating_markup 
            else:
                return remove_markup
    if(iden == 'userinfo'):
        if(count < len(user_ques_dict)):
            if(user_ques[count]['type'] == 'location'):
                return location_markup
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
def state(count, iden):
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
            return start(update,context) #after review , go back to /start menu again
        else:
            reply_text = "{}".format(get_question(count))
            update.message.reply_text(reply_text, reply_markup=keyboards(count , iden))
            return 'STATES{}'.format(count + 1)

    return _state

def user_info(count_info , iden):
    def _user_info(update, context):
        iden = 'userinfo'
        keyboard = [['END']]
        markup = ReplyKeyboardMarkup(keyboard)
        text = update.message.text
        user_id = update.message.from_user.id
        logger.info("input %s ", text)
        user_data = context.user_data

        # add data to memory in user_data dictionary
        if(count_info != 0 ):        
            key = get_userinfo_question_id(count_info-1)
            if(user_ques[count_info-1]['type'] == 'location'):
                location = geolocator.reverse("{},{}".format(update.message.location.latitude, update.message.location.longitude))
                user_data[key] = location.raw['address']['country_code']
                logger.info("input %f %f", update.message.location.latitude, update.message.location.longitude)
            else:
                user_data[key] = text
            question_info_list(user_data)

        # check if the count doesnt exceed the state's dict length
        # when it reaches the last state's dict, the conversation will end
        if(count_info == len(user_ques_dict)):
            reply_text = "Thanks! We have got your information. {}".format(question_info_list(user_data))
            update.message.reply_text(reply_text, reply_markup=markup)
            db.insert_user_info(user_id, user_data) #insert to db
            user_data.clear()
            return END
        else:
            reply_text = "{}".format(get_userinfo_question(count_info))
            update.message.reply_text(reply_text, reply_markup=keyboards(count_info, iden))
            return 'INFO{}'.format(count_info + 1)

    return _user_info

def start(update, context):
    rating_keyboard = [['Info'],['Review']]
    reply_text = "Welcome welcome welcome \n /review to start giving review \n /info to add info about yourself"
    rating_markup = ReplyKeyboardMarkup(rating_keyboard , one_time_keyboard=True)
    update.message.reply_text(reply_text)

    return SELECTING_OPTION 

def review_menu(update, context):
    print('review menu')
    reply_text = "first, /review to add your product name. then, \n /ask to start giving review" 
    update.message.reply_text(reply_text)

    return REVIEW

def validate_product(update , context):
    print('validate')
    reply_text = "This is to validate product name. \n What is your product name?" 
    update.message.reply_text(reply_text, reply_markup=ReplyKeyboardRemove(), one_time_keyboard=True)  
    return SEARCH

def do_search(update, context):
    print('search')
    text = update.message.text
    reply_text = "Do you mean {} ?".format(search_text(text))
    update.message.reply_text(reply_text, reply_markup=ReplyKeyboardRemove(), one_time_keyboard=True)  

    return RECEIVEDATA

 
def new_end(update, context):
    print("val end")
    # reply_text = "val end" 
    # update.message.reply_text(reply_text)
    return NEXT

def end(update, context):
    print('end')
    reply_text = "end" 
    update.message.reply_text(reply_text)
    return ConversationHandler.END

def main():
    iden = 'review'

    updater = Updater(token=TOKEN , use_context=True)
    dispatcher = updater.dispatcher

    # update dictionary based on data (questions) in db
    # which will then used for the ConversationHandler's states
    for n in ques :
        states_dict['STATES{}'.format(n+1)] = [MessageHandler(msg_filter(n+1) , state((n+1), iden))]

    for m in user_ques:
        user_ques_dict['INFO{}'.format(m+1)] = [MessageHandler(info_msg_filter(m+1) , user_info((m+1), iden))]

    # third level conversation handler for product review 
    review_convo = ConversationHandler(
        entry_points=[MessageHandler(Filters.text('^NEXT$'), state(0, iden))], #start first question
        states = states_dict,
        fallbacks=[MessageHandler(Filters.regex('^DONE$') , new_end)],
        allow_reentry = True,
        map_to_parent={
            DONE : NEXT
        })


    # second level conversation handler for product name validation 
    product_validation_convo = ConversationHandler(
        entry_points=[CommandHandler('review' , validate_product)],
        states ={ SEARCH : [MessageHandler(Filters.text , do_search)],
                    RECEIVEDATA : [MessageHandler(Filters.regex('^No') , do_search),
                                MessageHandler(Filters.text('^Yes') , new_end)],
                    NEXT : [review_convo]
                },
        fallbacks=[MessageHandler(Filters.regex('^DONE$') , new_end)],
        allow_reentry = True,
        map_to_parent={
            DONE : SECOND_SHOWING
        })
        

    # second level conversation handler for user info 
    user_info_convo = ConversationHandler(
        entry_points=[CommandHandler('info' , user_info(0, iden))],
        states = user_ques_dict,
        fallbacks=[MessageHandler(Filters.regex('^END$') , end)],
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