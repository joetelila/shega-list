from telebot import types
import telebot
import datetime
from db_helper import DB_helper
from cmdHelper import commandHelper

TOKEN = "1231860504:AAEx9qZ8znwwdwwq8vOzxskLEGJCBeaSaWs"
bot = telebot.TeleBot(TOKEN)

db = DB_helper(bot)
db.create_userTable()
cmd = commandHelper(bot, db)

state = 0
@bot.message_handler(commands=["start"])
def send_welcome(message):
    global state
    state = 1 # state = 1 means the user is at the home page
    #db.sayHello()
    currentTime = datetime.datetime.now()
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=2)
    markup.add("Browse", "Search","Sell","Your Items","Wish Lists","Alert me","Help")
    msgStart = bot.send_message(message.chat.id, """\
Selam {0}, {1}.
Welcome to Shegalist. What would you like to do today?\
""".format(message.chat.first_name, greeting(currentTime)), reply_markup=markup, parse_mode="html",)


def greeting(currentTime):
    if(currentTime.hour < 12):
        return "good morning"
    elif 12 <= currentTime.hour < 18:
        return "good afternoon"
    else:
        return "good evening"

# Handles all text messages that match the regular expression
@bot.message_handler(regexp="[^\n]+")
def handle_message(message):
    global state
    listOfcommands = []
    if state==1:
        listOfcommands = ['Browse','Search','Sell','Your Items','Wish Lists','Alert me', 'Help']
        home_state_processor(message, listOfcommands)
    elif state == 2:
        register_city_process(message)
        return

def home_state_processor(message, listOfcommands):
    global state
    if message.text not in listOfcommands:
        bot.send_message(message.chat.id, "Sorry, I don't understand that.")
    elif message.text == "Browse":
        bot.send_message(message.chat.id, "calling the browse function.")
    elif message.text == "Search":
        bot.send_message(message.chat.id, "calling the Search function.")
    elif message.text == "Sell":
        state = 2
        cmd.sell(message)
    elif message.text == "Your Items":
        bot.send_message(message.chat.id, "calling the Your Items function.")
    elif message.text == "Wish Lists":
        bot.send_message(message.chat.id, "calling the wish lists function.")
    elif message.text == "Alert me":
        bot.send_message(message.chat.id, "calling the Alert me function.")
    elif message.text == "Help" :
        print("calling the help function")

def register_city_process(message):
    print(message.text)

def extract_unique_code(text):
	# extracts unique code for the sent or start commands
	return text.chat.id

bot.polling()
