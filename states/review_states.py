from acessories.exception_log import *
from acessories.questions import get_question , get_question_id
from acessories.keyboards import *
from states.get_incentives import *
from states.start import *
from acessories.keep_data import *
# different constraints for bot status
START_OVER , REVIEW_DATA  , INFO_DATA , INFO_EXISTED  , REVIEW_QUESTION , INFO_QUESTION , PRODUCT_LIST ,NUM , ATTEMPT_COUNTER , INCENTIVE, INCENTIE_ID = range(11)
# constraints for bot states identification
SHOWING , SELECTING_OPTION ,END , DONE ,SEARCH , RECEIVEDATA , NEXT , INCENTIVE_ID= range(8)

data_list = {}
save_list = {}

# callback function for MessageHandler in ConversationHandler
def state(count , review_ques , user_ques , review_ques_dict , user_ques_dict, db):
    def _state(update, context):
        text = update.message.text
        user_id = update.message.from_user.id
        user_data = context.user_data
        logger.info("input %s ", text)
        print(text)
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
            key = get_question_id(count-1, review_ques) # get question id from db
            # print(key)
            question = get_question(count-1, review_ques) # get question from db
            data_list[key] = text #store all key and answer to a list and then use as context.user_data[DATA] ..
            save_list[question] = text #store all question and answer into temporary dict
        save_list['name'] = product_name # store inside temporary dict
        save_data(save_list) # pass dict to show data function

        # check if the count doesnt exceed the state's dict length
        # when it reaches the last state's dict, the conversation will end
        if(count == len(review_ques_dict)):
            user_data[REVIEW_DATA] = data_list # set dict to context dict with constraint key          
            reply_text = "This is the review details you have give us. See you again!. {}".format(save_data(save_list))
            update.message.reply_text(reply_text, reply_markup=keyboards(count , context, review_ques, user_ques, review_ques_dict, user_ques_dict))

            user_data[ATTEMPT_COUNTER] +=1 # after each review, increment constraint by 1

            output = get_incentive(user_data[ATTEMPT_COUNTER] , product_id , user_data , db) #get incentive
            if(len(output) > 0):
                for i in output: # reply message according to how many incentive result it returns
                    reply_text = "{}".format(output[i]) 
                    update.message.reply_text(reply_text, reply_markup=keyboards(count , context, review_ques, user_ques, review_ques_dict, user_ques_dict))
            else: # if theres no incentive returned, send this message instead
                reply_text = "There's no incentive available for this review" 
                update.message.reply_text(reply_text, reply_markup=keyboards(count , context , review_ques, user_ques, review_ques_dict, user_ques_dict))

            for i in user_data[INCENTIVE_ID]: # get all incentives id from INCENTIVE constraint
                incentive_id[str(i)] = "{}".format(user_data[INCENTIVE_ID][i]) # save it into incentive_list dict to store in db
                user_data[user_data[INCENTIVE_ID][i]] += 1 # increment counter when it is used
                print('incentive counter' , user_data[user_data[INCENTIVE_ID][i]] , 'incentive id ' , i )

            db.insert_item(user_id, user_data[REVIEW_DATA], product_id, incentive_id) #insert to db
            save_list.clear() #clear the dict
            data_list.clear()
            return start(update,context) #after review , go back to /start menu again
        else:
            reply_text = "{}".format(get_question(count, review_ques))
            update.message.reply_text(reply_text, reply_markup=keyboards(count , context,  review_ques, user_ques ,  review_ques_dict, user_ques_dict))
            return 'STATES{}'.format(count + 1)

    return _state