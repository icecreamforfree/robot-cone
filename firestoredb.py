import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import uuid


class FirestoreDB:
    def __init__(self):
            # Use a service account
        cred = credentials.Certificate('secrets/cusreview.json')
        firebase_admin.initialize_app(cred)

        self.db = firestore.client()
        
    #write
    def insert_item(self, userID , user_data):
        #random id
        id = uuid.uuid1()

        answer = {}
        for i in user_data:
            answer[i] = user_data[i]

        data = {
            u'userID': userID,
            u'review answer': answer
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

if __name__ == '__main__':
    db = FirestoreDB().userinfo_question_id()


    