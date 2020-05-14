# different constraints for bot status
START_OVER , REVIEW_DATA  , INFO_DATA , INFO_EXISTED  , REVIEW_QUESTION , INFO_QUESTION , PRODUCT_LIST ,NUM , ATTEMPT_COUNTER , INCENTIVE = range(10)
# constraints for bot states identification
SHOWING , SELECTING_OPTION ,END , DONE ,SEARCH , RECEIVEDATA , NEXT , INCENTIVE_COUNTER= range(8)

def get_incentive(attempt_counter , product_id , user_data , db):
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