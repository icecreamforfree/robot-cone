import sqlalchemy as db
from sqlalchemy import *
import requests
import psycopg2
import uuid
import os
from dotenv import load_dotenv
load_dotenv()

URL_ADDON = os.getenv('DATABASE_URL_ADDON')

class postgresdb:
    def __init__(self) :
        try:
            #ORM connection
            self.engine = db.create_engine('postgresql+psycopg2://{}'.format(URL_ADDON))
            self.connection = self.engine.connect()
            self.metadata = MetaData(self.engine)
            print('success')
        except:
            print('connection unsuccesful')
        
    def create_tables(self):
        if not self.engine.dialect.has_table(self.engine , 'product'):
            product_table = Table('product', self.metadata ,
                                Column('product_id', String, primary_key=True, nullable=False),
                                Column('product_name', String),
                                Column('brand', String),
                                Column('price' , Float),
                                Column('salesURL' , String))

        if not self.engine.dialect.has_table(self.engine , 'review_question'):
            review_question_table = Table('review_question', self.metadata ,
                                        Column('review_question_id', String, primary_key=True, nullable=False),
                                        Column('question', String),
                                        Column('type', String(12)))
              
        if not self.engine.dialect.has_table(self.engine , 'user_question'):
            user_question_table = Table('user_question', self.metadata ,
                                    Column('user_question_id', String, primary_key=True, nullable=False),
                                    Column('question', String),
                                    Column('type', String(12)))

        if not self.engine.dialect.has_table(self.engine , 'user'):
            user_table = Table('user', self.metadata ,
                                Column('user_id', Integer, primary_key=True, nullable=False))
                                  

        if not self.engine.dialect.has_table(self.engine , 'incentive'):
            incentive_table = Table('incentive', self.metadata ,
                                Column('incentive_id', String, primary_key=True, nullable=False),
                                Column('code', String),
                                Column('start_date', Date),
                                Column('end_date' , Date),
                                Column('tc' , String),
                                Column('condition', String),
                                Column('product_id', String, ForeignKey('product.product_id')))
              

        if not self.engine.dialect.has_table(self.engine , 'review'):
            review_table = Table('review', self.metadata ,
                                Column('review_id', String, primary_key=True, nullable=False),
                                Column('product_id', String, ForeignKey('product.product_id')),
                                Column('question_id', String , ForeignKey('review_question.review_question_id')),
                                Column('answer' , String),
                                Column('user_id' , Integer, ForeignKey('user.user_id')))

        if not self.engine.dialect.has_table(self.engine , 'incentive_given'):                                
            incentive_given_table = Table('incentive_given', self.metadata ,
                                Column('id' , String, primary_key=True , nullable=False),
                                Column('incentive_id', String , ForeignKey('incentive.incentive_id')),
                                Column('user_id' , Integer, nullable=False),
                                Column('given_date', Date, nullable=False))

        if not self.engine.dialect.has_table(self.engine , 'user_info'):
            user_info_table = Table('user_info' , self.metadata,
                                Column('user_info_id' , String),
                                Column('question_id' , String , ForeignKey('user_question.user_question_id')),
                                Column('answer' , String),
                                Column('user_id' , Integer , ForeignKey('user.user_id')))

        self.metadata.create_all()
        print('done')


    def insert_item(self):
        products = Table('product', self.metadata , autoload=True , autoload_with=self.engine)

        # data from extenal API
        base_url = "http://makeup-api.herokuapp.com/api/v1/products.json"
        search_params = {
            'brand' : 'maybelline',
            'product_type' : 'foundation'
        }
        search_response = requests.get(base_url,headers='', params=search_params)

        for res in search_response.json():
            prod_name = res['name'],
            brand = res['brand'],
            price = res['price'],
            link = res['product_link']

            query = products.insert().values(product_id = str(uuid.uuid1()) , product_name = prod_name , brand = brand, price = price , salesURL = link) 
            result = self.connection.execute(query)

            print(prod_name , ' ' , brand , ' ' , price , ' ' , link)

        #insert to different tables
        incentives = Table('incentive', self.metadata , autoload=True , autoload_with=self.engine)
        query = incentives.insert().values(incentive_id = uuid.uuid1() , code = "nmlkjh9876" , start_date = "2020-05-01", end_date="2020-06-01", tc = "labour day", condition = "2" , product_id = "f30a0f61-979c-11ea-abb0-b4b686d97da5")

        review_ques = Table('review_question', self.metadata , autoload=True , autoload_with=self.engine)
        query = review_ques.insert().values(review_question_id = uuid.uuid1() , question = "How likely would u purchase again?" , type = "rating")
        
        user_ques = Table('user_question', self.metadata , autoload=True , autoload_with=self.engine)
        query = user_ques.insert().values(user_question_id = uuid.uuid1() , question = "Whould you like to share your location? , if yes please insert" , type = "location")

        result = self.connection.execute(query)

if __name__ == '__main__':
    db = postgresdb()
    # db.create_tables()
    db.insert_item()


