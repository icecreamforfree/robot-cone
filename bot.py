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
START_OVER , REVIEW_DATA  , INFO_DATA , INFO_EXISTED  , REVIEW_QUESTION , INFO_QUESTION , PRODUCT_LIST ,NUM , ATTEMPT_COUNTER , INCENTIVE = range(10)
# constraints for bot states identification
SHOWING , SELECTING_OPTION ,END , DONE ,SEARCH , RECEIVEDATA , NEXT , INCENTIVE_COUNTER= range(8)
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
    # print('count ', count)
    if(count-1 <= len(states_dict)):
        if(ques[count-1]['type'] == 'open_ended'):
            return Filters.text
        else:
            return Filters.regex('^(1|2|3|4|5|6|7|8|9|10)$')

def info_msg_filter(count):
    if(count-1 <= len(user_ques_dict)):
        if(user_ques[count-1]['type'] == 'open_ended'):
            return Filters.text
        else:
            return Filters.regex('^(1|2|3|4|5|6|7|8|9|10)$')

# to show data at the end
def save_data(save_list):
    data_list = list()

    for key, value in save_list.items():
        data_list.append('{} - {}'.format(key, value))

    return "\n".join(data_list).join(['\n', '\n'])

def get_incentive(attempt_counter , product_id , user_data):
    incentive_list = db.get_incentives()
    return_list = {}
    end_result = {}
    n = 0
    for incentive in incentive_list :
        dicts ={
                'start' : incentive_list[incentive]['start date'],
                'end' : incentive_list[incentive]['end date'],
                'code' : incentive_list[incentive]['code'],
                't&c' : incentive_list[incentive]['t&c'],
        }
        if incentive_list[incentive]['productID'] == product_id and incentive_list[incentive]['condition']['review attempted'] == attempt_counter :
            return_list[incentive] = dicts
            # start_date = "{}/{}/{}".format(start.year, start.month, start.day)
            # end_date = "{}/{}/{}".format(end.year, end.month, end.day)   
            #  
    user_data[INCENTIVE] = return_list # set INCENTIVE constraint to the list of incentives
    for i in user_data[INCENTIVE]: # for every incentive id in the list, use all data related to it 
        start_date = user_data[INCENTIVE][i]['start']
        end_date = user_data[INCENTIVE][i]['end']
        code = user_data[INCENTIVE][i]['code']
        tc = user_data[INCENTIVE][i]['t&c']
        end_result[n] = "CONGRATS CONGRATS CONGRATS!!! \nThis is your incentive code: {0}\nPlease use it from {1} to {2} \nTerms and Conditions: {3} \
            ".format( code , start_date, end_date , tc) # return this message as a reply_text in the bot
        n += 1

        if not user_data.get(i): # i = incentiveID . if it is the first incentiveID returned
            user_data[i] = 0    # set the counter to 0

    return end_result
        

# callback function for MessageHandler in ConversationHandler
def state(count):
    def _state(update, context):
        text = update.message.text
        user_id = update.message.from_user.id
        user_data = context.user_data
        logger.info("input %s ", text)

        product_name = user_data['name'] 
        product_id = db.get_product_id(product_name) 
        output = {}
        #constraints to identify review question
        user_data[REVIEW_QUESTION] = True 
        user_data[INFO_QUESTION] = False 
        incentive_id = {}
        n = 0
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

            user_data[ATTEMPT_COUNTER] +=1 # after each review, increment constraint by 1
 
            output = get_incentive(user_data[ATTEMPT_COUNTER] , product_id , user_data) #get incentive
            if(len(output) > 0):
                for i in output: # reply message according to how many incentive result it returns
                    reply_text = "{}".format(output[i]) 
                    update.message.reply_text(reply_text, reply_markup=keyboards(count , context))
            else: # if theres no incentive returned, send this message instead
                reply_text = "There's no incentive available for this review" 
                update.message.reply_text(reply_text, reply_markup=keyboards(count , context))

            for i in user_data[INCENTIVE]: # get all incentives id from INCENTIVE constraint
                incentive_id[str(n)] = "{}".format(i) # save it into incentive_list dict to store in db
                n += 1
                user_data[i] += 1 # increment counter when it is used
                print('incentive counter' , user_data[i] , 'incentive id ' , i )

            db.insert_item(user_id, user_data[REVIEW_DATA], product_id, incentive_id) #insert to db
            save_list.clear() #clear the dict
            data_list.clear()
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
                # data_list[key] = location.raw['address']['country_code']
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
            data_list.clear() 
            return start(update,context)
        else:
            reply_text = "{}".format(get_userinfo_question(count_info))
            update.message.reply_text(reply_text, reply_markup=keyboards(count_info , context))
            return 'INFO{}'.format(count_info + 1) 

    return _user_info

def start(update, context):
    if not context.user_data.get(ATTEMPT_COUNTER) : # on first attempt
        context.user_data[ATTEMPT_COUNTER] = 0  # set ATTEMPT_COUNTER to 0
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
    else: #if it exceed the text search result and if there is nothing in the list , bring back to validate_product 
        reply_text = "Product name doesn't exist. Please insert the correct product name again" # prompt user to insert product name again
        update.message.reply_text(reply_text, reply_markup=ReplyKeyboardRemove(), one_time_keyboard=True)
        user_data[START_OVER] = True 

        return validate_product(update , context)


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
    for n in ques :
        states_dict['STATES{}'.format(n+1)] = [MessageHandler(msg_filter(n+1) , state(n+1))]

    for m in user_ques:
        user_ques_dict['INFO{}'.format(m+1)] = [MessageHandler(info_msg_filter(m+1) , user_info(m+1))]

    # third level conversation handler for product review 
    review_convo = ConversationHandler(
        entry_points=[MessageHandler(Filters.text('^NEXT$'), state(0))], #start first question
        states = states_dict,
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
        entry_points=[CommandHandler('info' , user_info(0))],
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