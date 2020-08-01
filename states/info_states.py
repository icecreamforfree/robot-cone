from acessories.exception_log import *
from acessories.questions import get_userinfo_question , get_userinfo_question_id
from acessories.keyboards import *
from states.start import *
from acessories.keep_data import *
from geopy.geocoders import Nominatim
import logging 

#geocoding
geolocator = Nominatim(user_agent="icecreamforfree")
# different constraints for bot status
START_OVER , REVIEW_DATA  , INFO_DATA , INFO_EXISTED  , REVIEW_QUESTION , INFO_QUESTION , PRODUCT_LIST ,NUM , ATTEMPT_COUNTER , INCENTIVE = range(10)
# constraints for bot states identification
SHOWING , SELECTING_OPTION ,END , DONE ,SEARCH , RECEIVEDATA , NEXT , INCENTIVE_ID= range(8)

data_list = {}
save_list = {}

def location_mapping(update): # calculate long lat to get country code
    location = geolocator.reverse("{},{}".format(update.message.location.latitude, update.message.location.longitude))
    country_code = location.raw['address']['country_code']
    logger.info("input %f %f", update.message.location.latitude, update.message.location.longitude)
    return country_code

def user_info(count_info, review_ques , user_ques , review_ques_dict ,user_ques_dict, db):
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
            key = get_userinfo_question_id(count_info-1 , user_ques) # get question id from db
            question = get_userinfo_question(count_info-1 , user_ques) # get question from db
            # if the question type is location 
            # then calculate the long lat at the next update
            if(user_ques[count_info-1]['type'] == 'location'):  
                text = location_mapping(update)        # then calculate the long lat at the next update
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
            update.message.reply_text(reply_text, reply_markup=keyboards(count_info , context, review_ques , user_ques, review_ques_dict, user_ques_dict))
            db.insert_user_info(user_id, user_data[INFO_DATA]) #insert to db
            user_data[INFO_EXISTED] = True # constraint to check user attempts 
            save_list.clear() # clear temporary dict
            data_list.clear() 
            return start(update,context)
        else:
            reply_text = "{}".format(get_userinfo_question(count_info, user_ques))
            update.message.reply_text(reply_text, reply_markup=keyboards(count_info , context,  review_ques, user_ques ,  review_ques_dict, user_ques_dict))
            return 'INFO{}'.format(count_info + 1) 

    return _user_info