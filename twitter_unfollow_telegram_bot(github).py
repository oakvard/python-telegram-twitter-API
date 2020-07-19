from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import tweepy
from time import sleep
import ast
import logging
import sqlite3
from datetime import datetime

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)

logger = logging.getLogger(__name__)

# Twitter auth API

'''
Get your authentication credentials from Twtter developer
'''

consumer_key =
consumer_secret =
access_token =
access_secret =

auth = tweepy.OAuthHandler(consumer_key,consumer_secret)
auth.set_access_token(access_token,access_secret)

api = tweepy.API(auth)

def return_link(ide):
	'''
	This function returns link to Twitter profile for the user id input
	'''
	user = api.get_user(id = ide)
	l = str(user).split("_json=")[1]
	m = l.split(', id')[0]
	usrnm = ast.literal_eval(m)['screen_name']
	url = 'https://twitter.com/'+usrnm
	return url

# Commands and messages for Telegram bot
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hello, welcome! type /help to know how this works.')

def help_command(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('type your Twitter username without @ to register. After registration type username again to check if someone has unfloowed you')

def check_user(update,context):
	'''
	Main command which takes user_name as input and adds user to db or if already exists returns unfolowers since last check.
	'''
    conn = sqlite3.connect('main.db')
    c = conn.cursor()
    user = (update.message.text.lower(),)
    user_name = update.message.text.lower()
    print(user_name)

    try :
        print('try')
        c.execute("SELECT EXISTS (SELECT 1 FROM FOLLOWERS WHERE name=?)",user)
        val = c.fetchone()[0]
        print(val)
        if val == 1:
            update.message.reply_text('Checking unfollowers')
            try :
                new  = api.followers_ids(screen_name =user_name)
            except : print('error')
            c.execute("SELECT followers FROM FOLLOWERS where name=?",user)
            followers_list = ast.literal_eval(c.fetchone()[0])
            #print(followers_list)
            for i in followers_list :
                if i not in new : 
                    u = return_link(i)
                    m = (u + ' has unfollowed you since last check')
                    update.message.reply_text(m)
            now = datetime.now()
            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
            new_list = (str(api.followers_ids(screen_name =user_name)),dt_string,user_name,)
            #print(new_list)
            c.execute("UPDATE FOLLOWERS SET followers=?,upd_dt=? WHERE name =? ",new_list)
            conn.commit()
        elif val == 0 :
            print('else')
            now = datetime.now()
            print(now)
            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
            print(dt_string)
            add = (user_name, str(api.followers_ids(screen_name =user_name)), dt_string,)
            print('add')
            c.execute("INSERT INTO FOLLOWERS VALUES (?,?,?) ",add)
            conn.commit()
			#unfDict[user]=api.followers_ids(screen_name =user)
            update.message.reply_text('User Added')
        else : print('fail')
        update.message.reply_text('Done Checking')
    except :
        update.message.reply_text('User not found')


# Telegram API

tk = "your telegram token"

def main():

	'''
	driver function to run telegram bot commands
	'''
	print('started')
	updater = Updater(tk, use_context=True)
	dp = updater.dispatcher
	# commandhandlers to return info
	dp.add_handler(CommandHandler("start", start))
	dp.add_handler(CommandHandler("help", help_command))

	# messagehandler to take username inout from user
	dp.add_handler(MessageHandler(Filters.text, check_user))

	# start bot

	updater.start_polling()
	updater.idle()

if __name__ == '__main__':
    main()