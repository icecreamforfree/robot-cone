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
pipenv install 
```

### Pipenv peer dependencies
There are imcompatible versions in the resolved dependencies:
1.  requests==2.23.0 (from -r /tmp/pipenvog7ro2t7requirements/pipenv-r7iw7_js-constraints.txt (line 21))
2.  requests (from cachecontrol==0.12.6->-r /tmp/pipenvog7ro2t7requirements/pipenv-r7iw7_js-constraints.txt (line 33))
3.  requests<3.0,>=2.21 (from algoliasearch==2.3.0->-r /tmp/pipenvog7ro2t7requirements/pipenv-r7iw7_js-constraints.txt (line 4))
4.  requests<3.0.0dev,>=2.18.0 (from google-api-core==1.18.0->-r /tmp/pipenvog7ro2t7requirements/pipenv-r7iw7_js-constraints.txt (line 14))
5.  requests==2.7.0 (from telebot==0.0.3->-r /tmp/pipenvog7ro2t7requirements/pipenv-r7iw7_js-constraints.txt (line 18))

### Environment variables set up
- Create an .env file in the directory
- add python-dotenv lib and os to get access to the variables  

Variables description :
1. TELE_TOKEN. Token for Telegram Bot
2. ALGOLIA_APP_ID. Algolia Application ID for data search 
3. ALGOLIA_ADMIN_API_KEY. Algolia API key for an application
4. ALGOLIA_INDEX_NAME. Algolia index name for keeping/storing data from db

## Python Telegram Bot Setup
It is a library provides a pure Python interface for Telegram Bot API.
First, generate an access token by talking to [BotFather](https://t.me/botfather) by following these steps https://core.telegram.org/bots#6-botfather. Now you are ready to create the bot!
There are two most important classes in the bot:
1. Updater 
    it continuously fetches all updates from telegram and passes them to Dispatcher
2. Dispatcher
    Updater object will then create a Dispathcer and link them with a Queue.
    User will then register handlers in the Dispatcher which will sort the updates fetched by the Updater and deliver back a callback function


Handlers that were used :
1. CommandHandler  
Handler class to handle Telegram commands
2. MessageHandler  
Handler class to handle Telegram messages such as text, media or status update
3. ConversationHandler  
Handler class to hold a conversation with a single user

## Getting Updates from Telegram Bot
There are two methods to receive updates from bot:
1.  Polling (getUpdates)
    This method works by keep pulling request from telegram server. After adding all the classes with handlers and callback functions, the bot is started by using polling method 
2.  Webhook
    Whenever there is an update from the bot, webhook will send HTTP POST request to the specified url, containing JSON format data. In this program, Server model that is used is Webhook with Reverse Proxy and Integrated server. These are the steps to setup webhook with this method:
    1.  Get a public IP (Nginx) with domain name. In this case, a VPS is used. [DigitalOcean](https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu-16-04), [Nginx](https://www.digitalocean.com/community/tutorials/how-to-install-nginx-on-ubuntu-18-04)
    2.  Get CA verified SSL certificate with [Letsencrypt](https://letsencrypt.org/getting-started/) and [CertBot](https://certbot.eff.org/lets-encrypt/ubuntuxenial-nginx)). Refer to this [link](https://haydenjames.io/how-to-set-up-an-nginx-certbot/) for the steps
    3.  Setup Reverse proxy with Nginx following this [wiki](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks#using-nginx-with-one-domainport-for-all-bots) page
    4.  Set Webhook to handle bot with [setWbhook](https://core.telegram.org/bots/api#setwebhook) and check bot [getWebhookInfo](https://core.telegram.org/bots/api#setwebhook) to verify if it is done successfully
    5.  Use integrated server in bot that listen to a local address an port following this [wiki](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks#using-nginx-with-one-domainport-for-all-bots) page


## Databases
### Firestore 
To setup Cloud Firestore follow these steps:
1. Create a project in [Firestore console](https://console.firebase.google.com/u/0/)    
2. Navigate to Database section and create a database
3. Set up environment by installing the required dependencies and library
4. Initialize Cloud Firestore SDK by using Firebase Admin SDK on your server
    - go to project settings and navigate to Service accounts tab
    - generate new private key (a json file will be donwloaded to your local disk and is ready to use)
5. You are ready to add and get data!

Implement firestore into your program:
1.  set the private key in json file as credential and initialize it
    ```py
    credentials.Certificate('./secrets/cusreview.json')
    firebase_admin.initialize_app(cred)
    ```
2.  assign a variable as firestore client
    ```py
    db = firestore.client()
    ```
3.  More information of what to do next at [Firestore](https://firebase.google.com/docs/firestore/quickstart)


### Postgresql 
Database Setup in WIndows can be found here [PostgreSQL](https://www.postgresqltutorial.com/install-postgresql/)

Database Setup in linux:
1.  Create the file /etc/apt/sources.list.d/pgdg.list and add a line for the repository
    ```sh
    sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
    ```
2.  Import the repository signing key 
    ```sh
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
    ```
3.  Update package lists and install packages
    ```sh
    sudo apt-get update
    apt-get install postgresql-12
    ```
4.  Start database server using:
    ```sh
    sudo systemctl start postgresql@12-main
    ```
5.  Check database server status
    ```sh
    sudo systemctl status postgresql
    ```
6.  Now, you can access into postgresql account. You are able to implement any psql shell command after using:
    ```sh
    sudo -u postgres psql
    ```



### Mongodb
Database setup in Windows can be found here [MongoDB](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-windows/)

Database setup in Linux:
1.  Import the public key used by the package management system
    ```sh
    wget -qO - https://www.mongodb.org/static/pgp/server-4.2.asc | sudo apt-key add -
    ```
    if you receive any error indicating gnupg is not installed, install gnupg before importing the private key
    ```sh
    sudo apt-get install gnupg
    ```
2.  Create list file for Mongodb for Ubuntu (Bionic)
    ```sh
    echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu bionic/mongodb-org/4.2 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.2.list
    ```
3.  Reload local packages database and install database, database directories will be at /var/lib/mongodb
    ```sh
    sudo apt-get update
    sudo apt-get install -y mongodb-org
    ```
4.  Start Mongodb server with systemctl
    ```sh
    sudo systemctl start mongod
    ```
5.  You can verify Mongodb has started successfully
    ```sh
    sudo systemctl status mongod
    ```
6.  Now, you can begin using Mongodb using:
    ```sh
    mongo
    ```

# How to run
1.  Spawns a shell within the virtualenv. Run
    ```sh
    piepnv shell
    ```
2.  Run this command to start the bot
    ```sh
    python bot.py
    ```
3.  Ctrl+C to stop

# Strore Data
1.  Use context.user_data in the handler callback to access to user-specific dict
2.  Load any value into this dictionary to temporary store information for later use
3.  Import the class function from files in db folder to bot.py
4.  After all questions are answered, this dictionary will be used to save into the respective database 


# Algolia Text Search
1. import algoliasearch module 
2. create variables client to create a search client by validating algolia Admin API and Application ID
3. create variable index to browse through an index name
4. use Search method to query an index
5. return desired data by following the response format in JSON 

