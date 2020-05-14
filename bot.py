from telebot import types
import telebot
import datetime
from db_helper import DB_helper
from cmdHelper import commandHelper

TOKEN = "1231860504:AAEx9qZ8znwwdwwq8vOzxskLEGJCBeaSaWs"
bot = telebot.TeleBot(TOKEN)

db = DB_helper(bot)
db.create_userTable()
db.create_productTable()
cmd = commandHelper(bot, db)

# global variables

userForm = {}
productForm = {}
photos = []

@bot.message_handler(commands=["start"])
def send_welcome(message):
    db.update_state(1, message) # state = 1 means the user is at the home page
    #db.sayHello()
    currentTime = datetime.datetime.now()
    db.saveuser(message)
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
    state = db.get_user_state(message)
    listOfcommands = []
    if state==1:  # home or start
        listOfcommands = ['Browse','Search','Sell','Your Items','Wish Lists','Alert me', 'Help']
        home_state_processor(message, listOfcommands)
    elif state == 2:  # sell state
        listOfcommands = ['Back'] # you can check here if the dictionaty alredy has some info before!
        collect_user_city(message, listOfcommands)
    elif state == 3: # share contact state
        listOfcommands = ['Main Menu']
        shareContact_state(message, listOfcommands)
    elif state == 4: # category list
        listOfcommands = ['Electronics','Clothing','Furnitures','Books','Jewelries','Accessories','Watches','Others','Cancel']
        selectCategories_state(message,listOfcommands)
    elif state == 5: # receive photo home_state_processor
        listOfcommands = ["Back", "Finish Sending"]
        receivePhoto_state(message,listOfcommands)
    else:
        print("state unknown")

@bot.message_handler(content_types=['photo'])
def handle_docs_audio(message):
    state = db.get_user_state(message)
    global userForm
    global photos
    if state == 5:
        photos.append(message.photo[-1].file_id)
        if len(photos) == 3:
            bot.send_message(message.chat.id, "Finished sending photos")
            db.update_state(6, message)
        elif len(photos) == 2:
            bot.send_message(message.chat.id, "Nice :), One more. or click Finish")
        elif len(photos) == 1:
            bot.send_message(message.chat.id, "Tips: You can send upto 3 pictures. click Finish when you're done")

    else:
        bot.send_message(message.chat.id, "Sorry, I don't need that now.")


@bot.message_handler(content_types=['contact']) # independant handler if the contact is shared!
def collect_phone_detail(message):
    state = db.get_user_state(message)
    global userForm
    if state == 3:
        userForm["phone"] = message.contact.phone_number
        db.register_user(userForm,message)
        cmd.sell(message)
    else:
        bot.send_message(message.chat.id, "Sorry, I don't need that now.")


def home_state_processor(message, listOfcommands):

    if message.text not in listOfcommands:
        bot.send_message(message.chat.id, "Sorry, I don't understand that.")
    elif message.text == "Browse":
        bot.send_message(message.chat.id, "calling the browse function.")
    elif message.text == "Search":
        bot.send_message(message.chat.id, "calling the Search function.")
    elif message.text == "Sell":
        db.update_state(2, message)
        sell_home = cmd.sell(message)
        print(sell_home)
    elif message.text == "Your Items":
        bot.send_message(message.chat.id, "calling the Your Items function.")
    elif message.text == "Wish Lists":
        bot.send_message(message.chat.id, "calling the wish lists function.")
    elif message.text == "Alert me":
        bot.send_message(message.chat.id, "calling the Alert me function.")
    elif message.text == "Help" :
        print("calling the help function")

def selectCategories_state(message,listOfcommands):
    if message.text not in listOfcommands:
        bot.send_message(message.chat.id, "Sorry, I don't understand that.")
    elif message.text == "Electronics":
        productForm["cat"] = message.text
        db.update_state(5, message)
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=2, resize_keyboard=True)
        markup.add("Back","Finish Sending")
        msgStart = bot.send_message(message.chat.id, """\
    Good:), Now send me some photos of your {0}. Eg. click 📎.\
    """.format(message.text.lower()), reply_markup=markup, parse_mode="html",)

    elif message.text == "Clothing":
        bot.send_message(message.chat.id, "you are selling clothing")
    elif message.text == "Furnitures":
        bot.send_message(message.chat.id, "you are selling Furnitures")
    elif message.text == "Books":
        bot.send_message(message.chat.id, "You are selling books")
    elif message.text == "Jewelries":
        bot.send_message(message.chat.id, "You are selling Jewelries")
    elif message.text == "Accessories":
        bot.send_message(message.chat.id, "You are selling accessories")
    elif message.text == "Watches" :
        bot.send_message(message.chat.id, "You are selling Watches")
    elif message.text == "Others" :
        bot.send_message(message.chat.id, "You are selling Others")
    elif message.text == "Cancel" :
        bot.send_message(message.chat.id, "You are cancelling the process")

def receivePhoto_state(message,listOfcommands):
    global photos
    if message.text not in listOfcommands:
        bot.send_message(message.chat.id, "Sorry, I don't understand that.")
    elif message.text == "Back":
        bot.send_message(message.chat.id, "You chose to be back")
    elif message.text == "Finish Sending":
        print(photos)
        bot.send_message(message.chat.id, "You finished submitting pictures")




def collect_user_city(message,listOfcommands):
    global userForm
    global state
    if message.text == "Back":
        send_welcome(message)
    else:
        userForm["city"] = message.text
        db.update_state(3, message)
        cmd.accept_user_number(message)

def shareContact_state(message, listOfcommands):
    if message.text  in listOfcommands:
        if message.text == "Main Menu":
            send_welcome(message)
    else:
        bot.send_message(message.chat.id, "Sorry, I don't understand that.")

def extract_unique_code(text):
	# extracts unique code for the sent or start commands
	return text.chat.id

bot.polling()
