from telegram import ReplyKeyboardMarkup
# different constraints for bot status
START_OVER , REVIEW_DATA  , INFO_DATA , INFO_EXISTED  , REVIEW_QUESTION , INFO_QUESTION , PRODUCT_LIST ,NUM , ATTEMPT_COUNTER , INCENTIVE = range(10)
# constraints for bot states identification
SHOWING , SELECTING_OPTION ,END , DONE ,SEARCH , RECEIVEDATA , NEXT , INCENTIVE_ID= range(8)

def start(update, context):
    if not context.user_data.get(ATTEMPT_COUNTER) : # on first attempt
        context.user_data[ATTEMPT_COUNTER] = 0  # set ATTEMPT_COUNTER to 0
    rating_keyboard = [['Info'],['Review']]
    reply_text = "Welcome welcome welcome \n /review to start giving review \n /info to add info about yourself"
    rating_markup = ReplyKeyboardMarkup(rating_keyboard , one_time_keyboard=True)
    update.message.reply_text(reply_text)

    return SELECTING_OPTION 