# robot-cone

## Intoduction 
Simple customer review bot

## Tech 
- [Python Telegram Bot](https://github.com/python-telegram-bot/python-telegram-bot)

## Bot's Commands
- Introduction - what does the bot do
- /start  - to start the bot
- /done - to stop the bot

## Flow chart 
https://sketchboard.me/ZB6AjLLmvIBv#/

## Intallation
Ensure that pip and python is installed

install pipenv for dependencies management. List of dependencies will be listed on Pipfile. Make sure that pipenv path is added to the system.
```sh
pip install --user pipenv
```

To install dependencies, use Pipfile
```sh
pipenv install Pipfile
```

### Environment variables set up
- Create an .env file in the directory
- add python-dotenv lib and os to get access to the variables  

Variables description :
1. TELE_TOKEN. Token for Telegram Bot

### Python Telegram Bot Setup
It is a library provides a pure Python interface for Telegram Bot API.
First, generate an access token by talking to [BotFather](https://t.me/botfather) by following these steps https://core.telegram.org/bots#6-botfather. Now you are ready to create the bot!
There are two most important classes in the bot:
1. Updater 
    it continuously fetches all updates from telegram and passes them to Dispatcher
2. Dispatcher
    Updater object will then create a Dispathcer and link them with a Queue.
    User will then register handlers in the Dispatcher which will sort the updates fetched by the Updater and deliver back a callback function

After adding all the classes with handlers and callback functions, the bot is started by using polling method 

Handlers that were used :
1. CommandHandler  
Handler class to handle Telegram commands
2. MessageHandler  
Handler class to handle Telegram messages such as text, media or status update
3. ConversationHandler  
Handler class to hold a conversation with a single user

### Firestore 
To setup Cloud Firestore follow these steps:
1. Create a project in [Firestore console](https://console.firebase.google.com/u/0/)    
2. Navigate to Database section and create a database
3. Set up environment by installing the required dependencies and library
4. Initialize Cloud Firestore SDK by using Firebase Admin SDK on your server
    - go to project settings and navigate to Service accounts tab
    - generate new private key (a json file will be donwloaded to your local disk and is ready to use)
5. You are ready to add and get data!
