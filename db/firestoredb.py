import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import uuid
import requests
import json


class FirestoreDB:
    def __init__(self):
            # Use a service account
        cred = credentials.Certificate('secrets/cusreview.json')
        firebase_admin.initialize_app(cred)

        self.db = firestore.client()
        
    #write
    def insert_item(self, userID , user_data, product_id, incentive_id):
        #random id
        id = uuid.uuid1()

        data = {
            u'userID': userID,
            u'productID' : product_id,
            u'review answer': user_data,
            u'incentiveID' : incentive_id
        }
        doc_ref = self.db.collection(u'review').document(str(id))
        doc_ref.set(data)

    def insert_user_info(self, userID , user_data):
        info = {}
        for i in user_data:
            info[i] = user_data[i]

        data = {
            u'user info': info
        }
        doc_ref = self.db.collection(u'user').document(u'{}'.format(userID))
        doc_ref.set(data)

    #read
    def get_question(self):
        # print(users_ref.id)
        users_ref = self.db.collection(u'question')
        docs = users_ref.stream()
        review_question = {}
        i = 0
        for doc in docs:
            review_question[i] = doc.to_dict()
            # print(u'{} => {}'.format(doc.id, doc.to_dict()))
            i += 1
        
        return review_question

    #read
    def get_question_id(self):
        users_ref = self.db.collection(u'question')
        docs = users_ref.stream()
        id = {}
        i = 0
        for doc in docs :
            id[i] = doc.id
            i += 1
        
        return id

    def userinfo_question(self):
        users_ref = self.db.collection(u'userQuestion')
        docs = users_ref.stream()
        user_question = {}
        i = 0
        for doc in docs:
            user_question[i] = doc.to_dict()
            # print(u'{} => {}'.format(doc.id, doc.to_dict()))
            i += 1
        # print(user_question)
        return user_question

    def userinfo_question_id(self):
        users_ref = self.db.collection(u'userQuestion')
        docs = users_ref.stream()
        id = {}
        i = 0
        for doc in docs :
            id[i] = doc.id
            i += 1
        # print(id)
        return id

    def insert_product(self):
        id = uuid.uuid1()
        base_url = "http://makeup-api.herokuapp.com/api/v1/products.json"
        search_params = {
            'brand' : 'maybelline',
            'product_type' : 'lipstick'
        }
        search_response = requests.get(base_url,headers='', params=search_params)
        # if search_response.status_code == 200 :
        arr = {}
        i = 0
        for res in search_response.json():
            # print(res)
            arr[i] = res
            i += 1
        # for a in arr:
        #     print(arr[a]['name'])

        doc_ref = self.db.collection(u'product').document(u'{}'.format(str(id)))
        doc_ref.set({
            u'name': arr[4]['name'],
            u'brand' : arr[4]['brand'],
            u'price' : arr[4]['price'],
            u'salesURL' : arr[4]['product_link']
        })
    
    # return product id
    def get_product_id(self, name):
        users_ref = self.db.collection(u'product')
        docs = users_ref.stream()
        products = {}
        for doc in docs :
            products[doc.id] = doc.to_dict()
            
        for i in products: 
            if products[i]['name'] == name: # get product name by comparing text search result and db data 
                return i

    def get_incentives(self):
        users_ref = self.db.collection(u'incentive')
        docs = users_ref.stream()
        incentive = {}
        for doc in docs :
            incentive[doc.id] = doc.to_dict()
            
        return incentive
        
     
if __name__ == '__main__':
    db = FirestoreDB().get_incentives()


    