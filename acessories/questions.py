#return question id
def get_question_id(count, review_ques_id):
    # if count <= len(review_ques_id):
    # for i in review_ques_id :
        # print('get ques ' , i , ' ', review_ques_id[i])
    return review_ques_id[count]


# return question
def get_question(count, review_ques):
    if count < len(review_ques):
        return review_ques[count]['question']

def get_userinfo_question_id(count, user_ques_id):
    if count < len(user_ques_id):
        return user_ques_id[count]
    
# return question
def get_userinfo_question(count, user_ques):
    if count < len(user_ques):
        return user_ques[count]['question']


