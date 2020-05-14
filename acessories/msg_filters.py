from telegram.ext import Filters
# return the correct filters for MessageHandler 
def msg_filter(count, review_ques, review_ques_dict):
    if(count-1 <= len(review_ques_dict)):
        if(review_ques[count-1]['type'] == 'open_ended'):
            return Filters.text
        else:
            return Filters.regex('^(1|2|3|4|5|6|7|8|9|10)$')

def info_msg_filter(count,user_ques, user_ques_dict):
    if(count <= len(user_ques_dict)):
        if(user_ques[count-1]['type'] == 'open_ended'):
            return Filters.text
        else:
            return Filters.regex('^(1|2|3|4|5|6|7|8|9|10)$')
