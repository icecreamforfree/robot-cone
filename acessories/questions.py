#return question id
def get_question_id(count, review_ques):
    return review_ques[count]['_id']

# return question
def get_question(count, review_ques):
    return review_ques[count]['question']

def get_userinfo_question_id(count, user_ques):
    return user_ques[count]['_id']
    
# return question
def get_userinfo_question(count, user_ques):
    return user_ques[count]['question']


