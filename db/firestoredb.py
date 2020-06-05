import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import uuid
import requests
import json
from datetime import *
today = date.today()
now = today.strftime("%Y/%m/%d")
start = datetime(2020,5,1).strftime("%Y/%m/%d")
end = datetime(2020,6,1).strftime("%Y/%m/%d")

class FirestoreDB:
    def __init__(self):
        try:
            # Use a service account
            cred = credentials.Certificate('./secrets/cusreview.json')
            firebase_admin.initialize_app(cred)
            self.db = firestore.client()
            print('success')
            print('FIRESTORE')
        except:
            print('unsuccessful')
        
    # save review data
    def insert_item(self, user_id , user_data, product_id, incentive_id):
        #random id
        id = uuid.uuid1()
        
        data = {
            u'user_id': user_id,
            u'product_id' : product_id,
            u'review answer': user_data,
            u'incentive_id' : incentive_id,
            u'incentive_given_date' : now
        }
        doc_ref = self.db.collection(u'review').document(str(id))
        doc_ref.set(data)

    # save user info
    def insert_user_info(self, user_id , user_data):
        data = {
            u'user info': user_data
        }
        doc_ref = self.db.collection(u'user').document(u'{}'.format(user_id))
        doc_ref.set(data)

    # insertion of first and second level data
    def initial_insert(self):
        arr = {}
        i = 0
        # get data from external api 
        base_url = "http://makeup-api.herokuapp.com/api/v1/products.json"
        search_params = {
            'brand' : 'maybelline',
            'product_type' : 'foundation'
        }
        search_response = requests.get(base_url,headers='', params=search_params)
        
        for res in search_response.json():
            product_id = str(uuid.uuid1())

            arr[i] = res
            product = {
                u'name': arr[i]['name'],
                u'brand' : arr[i]['brand'],
                u'price' : arr[i]['price'],
                u'salesURL' : arr[i]['product_link']
            }
            # insert in product collection
            prod = self.db.collection(u'product').document(u'{}'.format(product_id))
            # prod.set(product)

            incentive_dict = {
               'one ' : {u'product_id' : product_id,
                            u'code' : 'poiuy09876',
                            u'start_date' :start,
                            u'end_date':end,
                            u'tc':'no minimal purchase',
                            u'condition':'1'},
                'three' : { u'product_id' : product_id,
                            u'code': 'dfghhgf09876',
                            u'start_date' :start,
                            u'end_date':end,
                            u'tc':'mothers day',
                            u'condition':'2'}
            }
            for incen in incentive_dict: # insert incentive based on product_id
                incentive = self.db.collection(u'incentive').document(u'{}'.format(str(uuid.uuid1())))
                incentive.set(incentive_dict[incen])
            i += 1
            print('done')

        rev_q_dict = {
                'one':	{u'question': 'How would you rate this product'	, u'type': 'rating'},
                'two' : {u'question' :'State any product that you wish we carry'	, u'type':'open_ended'},
                'thre' : {u'question':'How would you rate our customer service'	, u'type':'rating'},
                'four' : {u'question':"How likely would u purchase again?"	,u'type':'rating'}
                }
        user_q_dict = {
                'one' : {u"question": "What is your hobby", u'type':	"open_ended"},
                'two' : {u'question':"What is your age"	,u'type':"open_ended"},
                'thre' : {u'question':"Whould you like to share your location? , if yes please insert", u'type':	"location"}
                }
        for rev in rev_q_dict: # inser review_question
                review = self.db.collection(u'review_question').document(u'{}'.format(str(uuid.uuid1())))
                review.set(rev_q_dict[rev])
                print('done1')
        for user in user_q_dict: # insert user_question
                users = self.db.collection(u'user_question').document(u'{}'.format(str(uuid.uuid1())))
                users.set(user_q_dict[user])
                print('done2')
   
    # get review question
    def review_question(self):
        # print(users_ref.id)
        users_ref = self.db.collection(u'review_question')
        docs = users_ref.stream()
        review_question = {}
        i = 0
        for doc in docs:
            review_question[i] = doc.to_dict()
            review_question[i].update({'_id':doc.id})
            i += 1
        for key, value in review_question.items():
            print(key , ' ' , value)

        return review_question

    # get user question
    def userinfo_question(self):
        users_ref = self.db.collection(u'user_question')
        docs = users_ref.stream()
        user_question = {}
        i = 0
        for doc in docs:
            user_question[i] = doc.to_dict()
            user_question[i].update({'_id':doc.id})
            i += 1
        for key, value in user_question.items():
            print(key , ' ' , value)
        return user_question

    # return product id
    def get_product_id(self, name):
        users_ref = self.db.collection(u'product').where(u'name', u'==', u'{}'.format(name))
        docs = users_ref.stream()
        for doc in docs :
            return doc.id

    # get incentive
    def get_incentives(self):
        users_ref = self.db.collection(u'incentive')
        docs = users_ref.stream()
        incentives = {}
        i = 0
        for doc in docs:
            incentives[i] = doc.to_dict()
            incentives[i].update({'_id':doc.id})
            i += 1
        # for key , value in incentives.items():
        #     print(key , ' ' , value)
        return incentives

if __name__ == '__main__':
    db = FirestoreDB().get_product_id("Maybelline Dream Smooth Mousse Foundation")


    