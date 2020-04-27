import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


class FirestoreDB:
    def __init__(self):
            # Use a service account
        cred = credentials.Certificate('secrets/cusreview.json')
        firebase_admin.initialize_app(cred)

        self.db = firestore.client()
        
    #write
    def insert_item(self, userID , user_data):
        answer = {}
        for i in user_data:
            answer[i] = user_data[i]

        data = {
            u'userID': userID,
            u'review answer': answer
        }
        doc_ref = self.db.collection(u'review').document(u'one')
        doc_ref.set(data)

    #read
    def get_question(self):
        # print(users_ref.id)
        users_ref = self.db.collection(u'question')
        docs = users_ref.stream()
        x = {}
        i = 0
        for doc in docs:
            x[i] = doc.to_dict()
            # print(u'{} => {}'.format(doc.id, doc.to_dict()))
            i += 1
        
        print(x)
        return x
        
    #read
    def get_question_id(self):
        users_ref = self.db.collection(u'question')
        docs = users_ref.stream()
        id = {}
        i = 0
        for doc in docs :
            id[i] = doc.id
            i += 1
        
        print(id)
        return id

if __name__ == '__main__':
    db = FirestoreDB()


    