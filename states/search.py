from telegram import ( ReplyKeyboardMarkup, KeyboardButton , ReplyKeyboardRemove) 
from others.text_search import search_text
# different constraints for bot status
START_OVER , REVIEW_DATA  , INFO_DATA , INFO_EXISTED  , REVIEW_QUESTION , INFO_QUESTION , PRODUCT_LIST ,NUM , ATTEMPT_COUNTER , INCENTIVE = range(10)
# constraints for bot states identification
SHOWING , SELECTING_OPTION ,END , DONE ,SEARCH , RECEIVEDATA , NEXT , INCENTIVE_COUNTER= range(8)

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