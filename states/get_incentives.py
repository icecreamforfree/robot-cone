# different constraints for bot status
START_OVER , REVIEW_DATA  , INFO_DATA , INFO_EXISTED  , REVIEW_QUESTION , INFO_QUESTION , PRODUCT_LIST ,NUM , ATTEMPT_COUNTER , INCENTIVE = range(10)
# constraints for bot states identification
SHOWING , SELECTING_OPTION ,END , DONE ,SEARCH , RECEIVEDATA , NEXT , INCENTIVE_ID= range(8)

def get_incentive(attempt_counter , product_id , user_data , db):
    incentive_list = db.get_incentives()
    return_list = {}
    end_result = {}
    id_list = {}
    id = 0
    for incentive in incentive_list :
        dicts ={
                'start' : incentive_list[incentive]['start_date'],
                'end' : incentive_list[incentive]['end_date'],
                'code' : incentive_list[incentive]['code'],
                't&c' : incentive_list[incentive]['tc'],
                'id' : incentive_list[incentive]['_id']
        }
        if incentive_list[incentive]['product_id'] == product_id and incentive_list[incentive]['condition'] == '{}'.format(attempt_counter) :
            return_list[incentive] = dicts
            id_list[id] = dicts['id']
            id +=1
             
    user_data[INCENTIVE] = return_list # set INCENTIVE constraint to the list of incentives
    user_data[INCENTIVE_ID] = id_list
    for i in user_data[INCENTIVE]: # for every incentive id in the list, use all data related to it 
        start_date = user_data[INCENTIVE][i]['start']
        end_date = user_data[INCENTIVE][i]['end']
        code = user_data[INCENTIVE][i]['code']
        tc = user_data[INCENTIVE][i]['t&c']
        end_result[i] = "CONGRATS CONGRATS CONGRATS!!! \nThis is your incentive code: {0}\nPlease use it from {1} to {2} \nTerms and Conditions: {3} \
            ".format( code , start_date, end_date , tc) # return this message as a reply_text in the bot
        i += 1

    for i in user_data[INCENTIVE_ID]:
        print('incentive ' ,i, user_data[INCENTIVE_ID][i])
        if not user_data.get(user_data[INCENTIVE_ID][i]): # if it is the first incentiveID --> user_data[INCENTIVE][i] returned
            user_data[user_data[INCENTIVE_ID][i]] = 0    # set the counter to 0 

    return end_result