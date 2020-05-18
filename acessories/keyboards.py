from telegram import (ReplyKeyboardMarkup, KeyboardButton , ReplyKeyboardRemove) 
# different constraints for bot status
START_OVER , REVIEW_DATA  , INFO_DATA , INFO_EXISTED  , REVIEW_QUESTION , INFO_QUESTION , PRODUCT_LIST ,NUM , ATTEMPT_COUNTER , INCENTIVE = range(10)
# constraints for bot states identification
SHOWING , SELECTING_OPTION ,END , DONE ,SEARCH , RECEIVEDATA , NEXT , INCENTIVE_COUNTER= range(8)
# return the correct type of keyboard for each type of questions
def keyboards(count , context,  review_ques, user_ques ,  review_ques_dict, user_ques_dict, question , db):
    rating_keyboard = [['1' , '2' , '3' , '4' , '5'],
                    ['6' , '7' , '8' , '9' , '10']]
    rating_markup = ReplyKeyboardMarkup(rating_keyboard , one_time_keyboard=True)
    end_keyboard = ['Yes' , 'No']
    end_markup = ReplyKeyboardMarkup(end_keyboard , one_time_keyboard=True)
    remove_markup = ReplyKeyboardRemove()
    location_keyboard = [[KeyboardButton(text="send_location", request_location=True)]]
    location_markup = ReplyKeyboardMarkup(location_keyboard)
    if context.user_data[REVIEW_QUESTION]: #check if it is review question, else it is info question
        if(count < len(review_ques_dict)):
        ### FOR FIRESTORE ###
        #     if(review_ques[count]['type'] == 'rating'):
        #         return rating_markup 
        #     else:
        #         return remove_markup

            if db.get_type(question) == 'rating':
                return rating_markup
            else:
                return remove_markup
        else: 
            return remove_markup
            
        
    else :  
        if(count < len(user_ques_dict)):
        ### FIRESTORE ###
        #     if(user_ques[count]['type'] == 'location'):
        #         return location_markup
        #     else:
        #         return remove_markup
            if db.get_user_type(question) == 'rating':
                return rating_markup
            elif db.get_user_type(question) == 'location':
                return location_markup
            else:
                return remove_markup
        else:
            return remove_markup