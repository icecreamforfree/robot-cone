from telegram.ext import (Updater , CommandHandler, MessageHandler, Filters, InlineQueryHandler,
                            CallbackQueryHandler, ConversationHandler)  #updater, dispatcher, handler
from telegram.error import (TelegramError, Unauthorized, BadRequest, TimedOut, ChatMigrated, NetworkError)
from telegram import (InlineQueryResultArticle, InputTextMessageContent, ReplyKeyboardMarkup,
                        KeyboardButton , InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove) 
import logging 
from firestoredb import FirestoreDB
import os
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv('TELE_TOKEN')

#handle exception
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

logger= logging.getLogger(__name__)

ONE , TWO , THREE , FOUR , FIVE = range(5)

# rating_keyboard = [
#         [InlineKeyboardButton(1 , callback_data='1'), InlineKeyboardButton(2 , callback_data='2'),
#         InlineKeyboardButton(3 , callback_data='3'),InlineKeyboardButton(4 , callback_data='4'),
#         InlineKeyboardButton(5 , callback_data='5'),InlineKeyboardButton(6 , callback_data='6'),
#         InlineKeyboardButton(7 , callback_data='7'),InlineKeyboardButton(8 , callback_data='8'),
#         InlineKeyboardButton(9 , callback_data='9'),InlineKeyboardButton(10 , callback_data='10')]]

# global
db = FirestoreDB()
ques = db.get_question()
ques_id = db.get_question_id()
states_dict = {}

# return the correct type of keyboard for each type of questions
def keyboards(count):
    rating_keyboard = [['1' , '2' , '3' , '4' , '5'],
                    ['6' , '7' , '8' , '9' , '10']]
    rating_markup = ReplyKeyboardMarkup(rating_keyboard , one_time_keyboard=True)
    end_keyboard = ['Yes' , 'No']
    end_markup = ReplyKeyboardMarkup(end_keyboard , one_time_keyboard=True)

    remove_markup = ReplyKeyboardRemove()
    if(count < len(states_dict)):
        if(ques[count]['type'] == 'rating'):
            return rating_markup 
        else:
            return remove_markup

#return question id
def get_question_id(count):
    return ques_id[count]

# return question
def get_question(count):
    return ques[count]['question']

def done(update, context):
    update.message.reply_text('Bye! Hope to hear form you again! /start to add more ')
    return ConversationHandler.END

def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Wrong Command! /start to get started")

# return the correct filters for MessageHandler 
def msg_filter(count):
    if(ques[count]['type'] == 'open_ended'):
        return Filters.text
    else:
        return Filters.regex('^(1|2|3|4|5|6|7|8|9|10)$')

def into_list(user_data):
    data_list = list()

    for key, value in user_data.items():
        data_list.append('{} - {}'.format(key, value))

    return "\n".join(data_list).join(['\n', '\n'])

# callback function for MessageHandler in ConversationHandler
def state(count):
    def _state(update, context):
        text = update.message.text
        user_id = update.message.from_user.id
        logger.info("input %s ", text)
        user_data = context.user_data

        #add data to memory in user_data dictionary
        if(count != 0 ):        
            key = get_question_id(count-1)
            user_data[key] = text
            into_list(user_data)

        # check if the count doesnt exceed the state's dict length
        # when it reaches the last state's dict, the conversation will end
        if(count == len(states_dict)):
            reply_text = "This is the review details you have give us. See you again!. {}".format(into_list(user_data))
            update.message.reply_text(reply_text, reply_markup=ReplyKeyboardRemove())
            db.insert_item(user_id, user_data) #insert to db
            return ConversationHandler.END
        else:
            reply_text = "{}".format(get_question(count))
            update.message.reply_text(reply_text, reply_markup=keyboards(count))
            return 'STATES{}'.format(count + 1)

    return _state

def main():
    # update dictionary based on data (questions) in db
    # which will then used for the ConversationHandler's states
    for n in ques :
        states_dict['STATES{}'.format(n+1)] = [MessageHandler(msg_filter(n) , state(n+1))]

    updater = Updater(token=TOKEN , use_context=True)
    dispatcher = updater.dispatcher
    conversation_handler = ConversationHandler(
        #the entry point start with the first question in db
        entry_points=[CommandHandler('start' , state(0))],
        states = states_dict,
        fallbacks=[CommandHandler('done', done)],
        allow_reentry = True)
    dispatcher.add_handler(conversation_handler)

    #wrong command
    wrong_command = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(wrong_command)

    #start bot
    updater.start_polling() 

    #to send stop signal to the bot
    updater.idle() 

if __name__ == '__main__':
    main()
