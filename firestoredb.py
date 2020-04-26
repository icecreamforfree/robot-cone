import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


class FirestoreDB:
    def __init__(self):
        # Use a service account
        cred = credentials.Certificate('secrets/cusreview.json')
        firebase_admin.initialize_app(cred)

        self.db = firestore.client()

    def insert_item(self):
        #write
        doc_ref = self.db.collection(u'users').document(u'')
        doc_ref.set({
            u'first': u'Alan',
            u'middle': u'Mathison',
            u'last': u'Turing',
            u'born': 1912
        })

    def get_item(self):
        #read
        users_ref = self.db.collection(u'question')
        docs = users_ref.stream()

        x = {}
        i = 0
        for doc in docs:
            x[i] = doc.to_dict()
            # print(u'{} => {}'.format(doc.id, doc.to_dict()))
            i += 1
        
        # print(x[1]['type'] == 'open_ended')
        return x

if __name__ == '__main__':
    FirestoreDB().get_item()
    