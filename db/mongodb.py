from pymongo import MongoClient
import requests
from datetime import *
import uuid
today = date.today()
now = today.strftime("%Y/%m/%d")

class MongoDB:
    def __init__(self):
        try:
            client = MongoClient('localhost' , 27017)
            self.db = client.robotcone
            print('success')
            print('MONGO')
        except:
            print('unsuccesful')

    # insertion of first and second level data
    def initial_insert(self):
        arr = {}
        i = 0
        base_url = "http://makeup-api.herokuapp.com/api/v1/products.json"
        search_params = {
            'brand' : 'maybelline',
            'product_type' : 'foundation'
        }
        search_response = requests.get(base_url,headers='', params=search_params)
        
        for res in search_response.json():
            product_id = str(uuid.uuid1())
            start = datetime(2020,5,1).strftime("%Y/%m/%d")
            end = datetime(2020,6,1).strftime("%Y/%m/%d")
            arr[i] = res
            product = {
                u'_id' : product_id,
                u'name': arr[i]['name'],
                u'brand' : arr[i]['brand'],
                u'price' : arr[i]['price'],
                u'salesURL' : arr[i]['product_link']
            }
            product = self.db.product.insert_one(product).inserted_id

            incentive_dict = {
               'one ' : {   
                            u'_id' : str(uuid.uuid1()),
                            u'product_id' : product_id,
                            u'code' : 'poiuy09876',
                            u'start_date' : start,
                            u'end_date': end,
                            u'tc':'no minimal purchase',
                            u'condition':'1'},
                'three' : { 
                            u'_id' : str(uuid.uuid1()),
                            u'product_id' : product_id,
                            u'code': 'dfghhgf09876',
                            u'start_date' : start,
                            u'end_date' : end,
                            u'tc':'mothers day',
                            u'condition':'2'}
            }
            for incen in incentive_dict:
                incentive = self.db.incentive.insert_one(incentive_dict[incen]).inserted_id
        rev_q_dict = {
                'one':	{u'_id': str(uuid.uuid1()), u'question': 'How would you rate this product'	, u'type': 'rating'},
                'two' : {u'_id': str(uuid.uuid1()), u'question' :'State any product that you wish we carry'	, u'type':'open_ended'},
                'thre' : {u'_id': str(uuid.uuid1()), u'question':'How would you rate our customer service'	, u'type':'rating'},
                'four' : {u'_id': str(uuid.uuid1()), u'question':"How likely would u purchase again?"	,u'type':'rating'}
                }
        user_q_dict = {
                'one' : {u'_id': str(uuid.uuid1()), u"question": "What is your hobby", u'type':	"open_ended"},
                'two' : {u'_id': str(uuid.uuid1()), u'question':"What is your age"	,u'type':"open_ended"},
                'thre' : {u'_id': str(uuid.uuid1()), u'question':"Whould you like to share your location? , if yes please insert", u'type':	"location"}
                }
        for rev in rev_q_dict: # inser review_question
                review = self.db.review_question.insert_one(rev_q_dict[rev]).inserted_id

        for user in user_q_dict: # insert user_question
                users = self.db.user_question.insert_one(user_q_dict[user]).inserted_id

    # save review data
    def insert_item(self, user_id , user_data, product_id, incentive_id):
        id = uuid.uuid1()
        data = {
            u'_id' : str(id),
            u'user_id': user_id,
            u'product_id' : product_id,
            u'review answer': user_data,
            u'incentive_id' : incentive_id,
            u'incentive_given_date' : now
        }
        review = self.db.review.insert_one(data).inserted_id
    
    def insert_user_info(self, user_id, user_data):
        id = uuid.uuid1()
        data = {
            u'_id' : user_id,
            u'user_info': user_data
        }
        # update on the user_id if exist
        user_info = self.db.user.update({"_id": user_id}, {'$set':data}, upsert=True)

    # get review question
    def review_question(self):
        docs = self.db.review_question.find()
        review_question = {}
        i = 0
        for doc in docs:
            review_question[i] = doc
            i+=1
        for key , value in review_question.items():
            print(key , ' ' , value)
        return review_question
    
    # get user info question
    def userinfo_question(self):
        docs = self.db.user_question.find()
        user_question = {}
        i = 0
        for doc in docs:
            user_question[i] = doc
            i += 1
        for key, value in user_question.items():
            print(key , ' ' , value)
        return user_question

    # return product id
    def get_product_id(self, name):
        docs = self.db.product.find({'name' : name}, {'_id' : 1})
        for doc in docs:
            # print(doc['_id'])
            return doc['_id']

    # get incentive
    def get_incentives(self):
        docs = self.db.incentive.find()
        incentives = {}
        i = 0
        for doc in docs:
            incentives[i] = doc
            i += 1
        for key , value in incentives.items():
            print(key , ' ' , value)
        return incentives

if __name__ == '__main__':
    db = MongoDB()
    # db.get_product_id("Maybelline Dream Smooth Mousse Foundation")
    # db.get_incentives()
    db.review_question()