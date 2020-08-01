import sqlalchemy as db
from sqlalchemy import *
import requests
import psycopg2
import uuid
from datetime import *
import os
from dotenv import load_dotenv
load_dotenv()
URL_ADDON = os.getenv('DATABASE_URL')

today = date.today()
now = today.strftime("%Y/%m/%d")
start = datetime(2020,5,1).strftime("%Y/%m/%d")
end = datetime(2020,6,1).strftime("%Y/%m/%d")

class PostgresDB:
    def __init__(self) :
        try:
            #ORM connection
            self.engine = db.create_engine('postgresql+psycopg2://{}'.format(URL_ADDON))
            self.connection = self.engine.connect()
            self.metadata = MetaData(self.engine)
            print('success')
            print('POSTGRESQL')
        except:
            print('connection unsuccesful')
        
    def create_tables(self):
        if not self.engine.dialect.has_table(self.engine , 'product'):
            product_table = Table('product', self.metadata ,
                                Column('_id', String, primary_key=True, nullable=False),
                                Column('product_name', String),
                                Column('brand', String),
                                Column('price' , Float),
                                Column('salesURL' , String))

        if not self.engine.dialect.has_table(self.engine , 'review_question'):
            review_question_table = Table('review_question', self.metadata ,
                                        Column('_id', String, primary_key=True, nullable=False),
                                        Column('question', String),
                                        Column('type', String(12)))
              
        if not self.engine.dialect.has_table(self.engine , 'user_question'):
            user_question_table = Table('user_question', self.metadata ,
                                    Column('_id', String, primary_key=True, nullable=False),
                                    Column('question', String),
                                    Column('type', String(12)))

        if not self.engine.dialect.has_table(self.engine , 'users'):
            user_table = Table('users', self.metadata ,
                                Column('user_id', Integer, primary_key=True, nullable=False))
                                  

        if not self.engine.dialect.has_table(self.engine , 'incentive'):
            incentive_table = Table('incentive', self.metadata ,
                                Column('_id', String, primary_key=True, nullable=False),
                                Column('code', String),
                                Column('start_date', Date),
                                Column('end_date' , Date),
                                Column('tc' , String),
                                Column('condition', String),
                                Column('product_id', String, ForeignKey('product._id')))
              

        if not self.engine.dialect.has_table(self.engine , 'review'):
            review_table = Table('review', self.metadata ,
                                Column('review_id', String, primary_key=True, nullable=False),
                                Column('product_id', String, ForeignKey('product._id')),
                                Column('question_id', String , ForeignKey('review_question._id')),
                                Column('answer' , String),
                                Column('user_id' , Integer, ForeignKey('users.user_id')))

        if not self.engine.dialect.has_table(self.engine , 'incentive_given'):                                
            incentive_given_table = Table('incentive_given', self.metadata ,
                                Column('id' , String, primary_key=True , nullable=False),
                                Column('incentive_id', String , ForeignKey('incentive._id')),
                                Column('user_id' , Integer,  ForeignKey('users.user_id')),
                                Column('given_date', Date, nullable=False))

        if not self.engine.dialect.has_table(self.engine , 'user_info'):
            user_info_table = Table('user_info' , self.metadata,
                                Column('user_info_id' , String, primary_key=True , nullable=False),
                                Column('question_id' , String , ForeignKey('user_question._id')),
                                Column('answer' , String),
                                Column('user_id' , Integer , ForeignKey('users.user_id')))

        self.metadata.create_all()
        print('done')


    def initial_insert(self):
        ind = uuid.uuid1()

        # variables for tables in psql
        products = Table('product', self.metadata , autoload=True , autoload_with=self.engine)
        incentives = Table('incentive', self.metadata , autoload=True , autoload_with=self.engine)
        review_ques = Table('review_question', self.metadata , autoload=True , autoload_with=self.engine)
        user_ques = Table('user_question', self.metadata , autoload=True , autoload_with=self.engine)
        users = Table('users', self.metadata , autoload=True , autoload_with=self.engine)

        incentive_dict = {
                'two' :   {'code': 'poiuy09876',	'start_date' :start, 'end_date':end	,'tc':'no minimal purchase', 'condition':'1'},	
                'three' : {'code': 'dfghhgf09876',	'start_date' :start, 'end_date':end	,'tc':'mothers day', 'condition':'2'}
                }
        rev_q_dict = {
                'one':	{'question': 'How would you rate this product'	, 'type': 'rating'},
                'two' : {'question' :'State any product that you wish we carry'	, 'type':'open_ended'},
                'thre' : {'question':'How would you rate our customer service'	, 'type':'rating'},
                'four' : {'question':"How likely would u purchase again?"	,'type':'rating'}
                }
        user_q_dict = {
                'one' : {"question": "What is your hobby", 'type':	"open_ended"},
                'two' : {'question':"What is your age"	,'type':"open_ended"},
                'thre' : {'question':"Whould you like to share your location? , if yes please insert", 'type':	"location"}
        }
        # data from extenal API
        base_url = "http://makeup-api.herokuapp.com/api/v1/products.json"
        search_params = {
            'brand' : 'maybelline',
            'product_type' : 'foundation'
        }
        search_response = requests.get(base_url,headers='', params=search_params)

        for res in search_response.json():
            product_id = uuid.uuid1()
            prod_name = res['name'],
            brand = res['brand'],
            price = res['price'],
            link = res['product_link']

            # insert to product table
            query = products.insert().values(_id = product_id , product_name = prod_name , brand = brand, price = price , salesURL = link) 
            result1 = self.connection.execute(query)
            print('inserted product')
            for i in incentive_dict: # insert to incentive table based on product_id
                incen_query = incentives.insert().values(_id = uuid.uuid1() , code = incentive_dict[i]['code'] , start_date = incentive_dict[i]['start_date'], end_date=incentive_dict[i]['end_date'], tc = incentive_dict[i]['tc'], condition = incentive_dict[i]['condition'] , product_id = product_id)
                result2 = self.connection.execute(incen_query)
                print('inserted incen')

        #insert to review question table
        for i in rev_q_dict:
            rev = review_ques.insert().values(_id = uuid.uuid1() , question = rev_q_dict[i]['question'] , type = rev_q_dict[i]['type'])
            result3 = self.connection.execute(rev)
            print('inserted rev q')
        #insert to user question table
        for i in user_q_dict:
            user = user_ques.insert().values(_id = uuid.uuid1() , question = user_q_dict[i]['question'] , type = user_q_dict[i]['type'])
            result4 = self.connection.execute(user)
            print('inserted user')
        #insert to user table
        # users = users.insert().values(user_id = 685948947)
        # result5 = self.connection.execute(users)
    
    # check if user id is existed
    def check_id(self, user_id):
        user = Table('users', self.metadata , autoload=True , autoload_with=self.engine)
        query = select([user.c.user_id]).where(user.c.user_id == user_id)
        results = self.connection.execute(query).fetchall()
        if results == []: # if id doesnt exist , add to user table
            usr = user.insert().values(user_id = user_id)
            result = self.connection.execute(usr)
            print('added')
            return

    # insert review data
    def insert_item(self, user_id , user_data, product_id, incentive_id):
        review = Table('review', self.metadata , autoload=True , autoload_with=self.engine)
        incentive_given = Table('incentive_given', self.metadata , autoload=True , autoload_with=self.engine)
        self.check_id(user_id) # check if id existed

        for data in user_data:
            reviews = review.insert().values(review_id = uuid.uuid1() , product_id = product_id , question_id = data , answer = user_data[data] , user_id = user_id)
            result = self.connection.execute(reviews)

        for i in incentive_id:
            print(i , ' ' , incentive_id[i])
            incentives = incentive_given.insert().values(id = uuid.uuid1() , incentive_id = incentive_id[i], user_id = user_id, given_date = now )
            result = self.connection.execute(incentives)

    # insert user info data
    def insert_user_info(self, user_id, user_data):
        uinfo = Table('user_info', self.metadata , autoload=True , autoload_with=self.engine)
        self.check_id(user_id)

        for data in user_data:
            info = uinfo.insert().values(user_info_id = uuid.uuid1() , question_id = data , answer = user_data[data] , user_id = user_id)
            result = self.connection.execute(info)


    def review_question(self):
        question = Table('review_question', self.metadata , autoload=True , autoload_with=self.engine)
        query = select([question])
        results = self.connection.execute(query).fetchall()
        review_question = {}
        i = 0
        for result in results:
            review_question[i] = {column:value for column, value in result.items()}
            i += 1
        
        # print(review_question[0]['type'])
        for key, value in review_question.items():
            print(key , ' ' , value)
        return review_question


    def userinfo_question(self):
        question = Table('user_question', self.metadata , autoload=True , autoload_with=self.engine)
        query = select([question])
        results = self.connection.execute(query).fetchall()
        user_question = {}
        i = 0
        for result in results:
            user_question[i] = {column:value for column, value in result.items()}
            i += 1

        # print(user_question[0]['type'])
        for i in user_question:
            print(i , user_question[i])
        return user_question

    
    def get_product_id(self, name):
        product = Table('product', self.metadata , autoload=True , autoload_with=self.engine)
        query = select([product.c._id]).where(product.c.product_name == name)
        result = self.connection.execute(query).fetchone()
        return result[0]
    
    def get_incentives(self):
        incentive = Table('incentive', self.metadata , autoload=True , autoload_with=self.engine)
        query = select([incentive])
        results = self.connection.execute(query).fetchall()
        incentives = {}
        i = 0
        for result in results:
            incentives[i] = {column:value for column, value in result.items()}
            i += 1
        # print(user_question[0]['type'])
        # for i in incentives:
        #     print(i , incentives[i])
        return incentives


if __name__ == '__main__':
    db = PostgresDB()
    # db.create_tables()
    # db.insert_item(685948987)
    # db.insert_item('685948947' , 'f30a0f61-979c-11ea-abb0-b4b686d97da5')
    # db.get_type('0d2c9586-9860-11ea-8ca1-b4b686d97da5')
    # db.get_product_id('Maybelline Dream Smooth Mousse Foundation')
    # db.get_incentives()
    # db.initial_insert()
    db.review_question()


