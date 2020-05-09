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


# different constraints for bot status
START_OVER , REVIEW_DATA  , INFO_DATA , INFO_EXISTED  , REVIEW_QUESTION , INFO_QUESTION , PRODUCT_LIST , NUM = range(8)
# constraints for bot states identification
SHOWING , SELECTING_OPTION ,END , DONE ,SEARCH , RECEIVEDATA , NEXT = range(7)

# global
db = FirestoreDB()
ques = db.get_question()
ques_id = db.get_question_id()
states_dict = {}
user_ques = db.userinfo_question()
user_ques_id = db.userinfo_question_id()
user_ques_dict = {}
#additional dict to store data
data_list = {}
# info_list = {}
save_list ={}

# return the correct type of keyboard for each type of questions
def keyboards(count, context):
    rating_keyboard = [['1' , '2' , '3' , '4' , '5'],
                    ['6' , '7' , '8' , '9' , '10']]
    rating_markup = ReplyKeyboardMarkup(rating_keyboard , one_time_keyboard=True)
    end_keyboard = ['Yes' , 'No']
    end_markup = ReplyKeyboardMarkup(end_keyboard , one_time_keyboard=True)
    remove_markup = ReplyKeyboardRemove()
    location_keyboard = [[KeyboardButton(text="send_location", request_location=True)]]
    location_markup = ReplyKeyboardMarkup(location_keyboard)
    if context.user_data[REVIEW_QUESTION]: #check if it is review question, else it is info question
        if(count < len(states_dict)):
            if(ques[count]['type'] == 'rating'):
                return rating_markup 
            else:
                return remove_markup
        else: 
            return remove_markup
    else :  
        if(count < len(user_ques_dict)):
            if(user_ques[count]['type'] == 'location'):
                return location_markup
            else:
                return remove_markup
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

# to show data at the end
def save_data(save_list):
    data_list = list()

    for key, value in save_list.items():
        data_list.append('{} - {}'.format(key, value))

    return "\n".join(data_list).join(['\n', '\n'])

# callback function for MessageHandler in ConversationHandler
def state(count):
    def _state(update, context):
        text = update.message.text
        user_id = update.message.from_user.id
        user_data = context.user_data
        product_name = user_data['name'] 
        logger.info("input %s ", text)
        
        #constraints to identify review question
        user_data[REVIEW_QUESTION] = True 
        user_data[INFO_QUESTION] = False 

        #add data to memory in user_data dictionary
        if(count != 0 ):        
            key = get_question_id(count-1) # get question id from db
            question = get_question(count-1) # get question from db
            data_list[key] = text #store all key and answer to a list and then use as context.user_data[DATA] ..
            save_list[question] = text #store all question and answer into temporary dict
        save_list['name'] = product_name # store inside temporary dict
        save_data(save_list) # pass dict to show data function

        # check if the count doesnt exceed the state's dict length
        # when it reaches the last state's dict, the conversation will end
        if(count == len(states_dict)):
            user_data[REVIEW_DATA] = data_list # set dict to context dict with constraint key          
            reply_text = "This is the review details you have give us. See you again!. {}".format(save_data(save_list))
            update.message.reply_text(reply_text, reply_markup=keyboards(count , context))
            db.insert_item(user_id, user_data[REVIEW_DATA], db.get_product_id(product_name)) #insert to db
            save_list.clear() #clear the dict
            return start(update,context) #after review , go back to /start menu again
        else:
            reply_text = "{}".format(get_question(count))
            update.message.reply_text(reply_text, reply_markup=keyboards(count , context))
            return 'STATES{}'.format(count + 1)

    return _state

def user_info(count_info):
    def _user_info(update, context):
        text = update.message.text
        user_id = update.message.from_user.id
        logger.info("input %s ", text)
        user_data = context.user_data

        #constraints to identify info question
        user_data[INFO_QUESTION] = True
        user_data[REVIEW_QUESTION] = False

        # add data to memory in user_data dictionary
        if(count_info != 0 ):     
            key = get_userinfo_question_id(count_info-1) # get question id from db
            question = get_userinfo_question(count_info-1) # get question from db
            # if the question type is location 
            # then calculate the long lat at the next update
            if(user_ques[count_info-1]['type'] == 'location'):  
                location = geolocator.reverse("{},{}".format(update.message.location.latitude, update.message.location.longitude))
                save_list['location'] = data_list[key] = location.raw['address']['country_code'] # insert into temporary dict
                logger.info("input %f %f", update.message.location.latitude, update.message.location.longitude)
            else:
                data_list[key] = text # store into temporary dict
                save_list[question] = text 
            save_data(save_list)
        else: # check if it is user's first attempt and return text respectively
            if not user_data.get(INFO_EXISTED):
                reply_text = "Tell us about yourself!"
                update.message.reply_text(reply_text)
            else:
                reply_text = "Lets update your information!"
                update.message.reply_text(reply_text)
        

        # check if the count doesnt exceed the state's dict length
        # when it reaches the last state's dict, the conversation will end
        if(count_info == len(user_ques_dict)):
            user_data[INFO_DATA] = data_list
            reply_text = "Thanks! We have got your information. {}".format(save_data(save_list))
            update.message.reply_text(reply_text, reply_markup=keyboards(count_info , context))
            db.insert_user_info(user_id, user_data[INFO_DATA]) #insert to db
            user_data[INFO_EXISTED] = True # constraint to check user attempts 
            save_list.clear() # clear temporary dict
            return start(update,context)
        else:
            reply_text = "{}".format(get_userinfo_question(count_info))
            update.message.reply_text(reply_text, reply_markup=keyboards(count_info , context))
            return 'INFO{}'.format(count_info + 1) 

    return _user_info

def start(update, context):
    rating_keyboard = [['Info'],['Review']]
    reply_text = "Welcome welcome welcome \n /review to start giving review \n /info to add info about yourself"
    rating_markup = ReplyKeyboardMarkup(rating_keyboard , one_time_keyboard=True)
    update.message.reply_text(reply_text)

    return SELECTING_OPTION 

def validate_product(update , context): 
    user_data = context.user_data
    if not user_data.get(START_OVER): # check if this is user's first attempt
        reply_text = "This is to validate product name. \n What is your product name?"  
    else:
        reply_text = "What is your product name?" 
    update.message.reply_text(reply_text, reply_markup=ReplyKeyboardRemove(), one_time_keyboard=True)  

    # constraints to set for doing search 
    user_data[NUM] = 0
    user_data[START_OVER] = False

    return SEARCH

def do_search(update, context):
    # def _do_search(update,context):
    print('do seacrh')
    keyboard = [['Yes'] , ['No']]
    markup = ReplyKeyboardMarkup(keyboard)
    text = update.message.text
    user_data = context.user_data 
    if not user_data.get(START_OVER): # check if it is user's first attempt
        user_data[PRODUCT_LIST]= search_text(text) # is yes , store text search results into context dict 
    else:
        user_data[NUM] += 1 # if it is not first attempt, increment NUM constraint by 1
    
    if user_data[NUM] < len(user_data[PRODUCT_LIST]): # if the NUM constraint is within the number of text search result
        reply_text = "Do you mean {} ?".format(user_data[PRODUCT_LIST][user_data[NUM]]) # keep asking user for the text search result one by one
        update.message.reply_text(reply_text, reply_markup=markup, one_time_keyboard=True)
       
        user_data[START_OVER] = True # START_OVER constraint identifies not user's first attempt
        user_data['name'] = user_data[PRODUCT_LIST][user_data[NUM]] # store the text search result to 'name' constraint , it will be overwritten everytime it is set

        return RECEIVEDATA

    else: #if it exceed the text search result , bring back to validate_product 
        reply_text = "Please insert the correct product name again" # prompt user to insert product name again
        update.message.reply_text(reply_text, reply_markup=ReplyKeyboardRemove(), one_time_keyboard=True)
        user_data[START_OVER] = True 

        return validate_product(update , context)


def new_end(update, context):
    print("val end")
    keyboard = [['NEXT']]
    markup = ReplyKeyboardMarkup(keyboard)
    reply_text = "Click next to the review question" 
    update.message.reply_text(reply_text , reply_markup=markup , one_time_keyboard=True)
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
    for n in ques :
        states_dict['STATES{}'.format(n+1)] = [MessageHandler(msg_filter(n+1) , state(n+1))]

    for m in user_ques:
        user_ques_dict['INFO{}'.format(m+1)] = [MessageHandler(info_msg_filter(m+1) , user_info(m+1))]

    # third level conversation handler for product review 
    review_convo = ConversationHandler(
        entry_points=[MessageHandler(Filters.text('^NEXT$'), state(0))], #start first question
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
                    RECEIVEDATA : [MessageHandler(Filters.text('^No') , do_search),
                                MessageHandler(Filters.text('^Yes') , new_end)],
                    NEXT : [review_convo]
                },
        fallbacks=[MessageHandler(Filters.regex('^DONE$') , new_end)],
        allow_reentry = True,
        map_to_parent={
            DONE : SEARCH
        })
        

    # second level conversation handler for user info 
    user_info_convo = ConversationHandler(
        entry_points=[CommandHandler('info' , user_info(0))],
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