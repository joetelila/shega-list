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
    db.saveuser(message)
    if db.get_user_state(message):
        state = db.get_user_state(message)
    else:
        state = 1
    db.update_state(1, message) # state = 1 means the user is at the home page
    #db.sayHello()

    currentTime = datetime.datetime.now()
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=2)
    markup.add("Browse", "Search","Sell","Your Items","Wish Lists","Alert me","Help")

    if state == 8:
        msgStart = bot.send_message(message.chat.id, """\
    Welcome back, What would you like to do next?\
    """, reply_markup=markup, parse_mode="html",)
    else:
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
        listOfcommands = ["Cancel", "Finish Sending"]
        receivePhoto_state(message,listOfcommands)
    elif state == 6:  # recieve description state
        listOfcommands = ["Main Menu"]
        receive_description_state(message, listOfcommands)
    elif state == 7:  # receive product price
        listOfcommands = ["Main Menu"]
        receive_price_state(message, listOfcommands)
    elif state == 8: # state to recieve user location
        listOfcommands = ["Main Menu"]
        receive_location_state(message, listOfcommands)
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
            db.update_state(6, message) # 6 state is for accepting description
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=2, resize_keyboard=True)
            markup.add("Main Menu","Help")
            msgStart = bot.send_message(message.chat.id, """\
    Please send me product description,

    Eg. Seagate External hard disk
        1TB (Tera byte)
        2 months warranty
\
        """, reply_markup=markup, parse_mode="html",)

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

@bot.message_handler(content_types=['location']) # independant handler if the contact is shared!
def collect_phone_detail(message):
    global productForm
    global photos
    state = db.get_user_state(message)
    if state == 8:
        productForm["location"] = ""+str(message.location.longitude)+","+str(message.location.latitude)
        print(productForm)
        bot.send_message(message.chat.id, "Done!, Your product has been submitted for approval.")
        db.add_new_product(message, photos, productForm)
        send_welcome(message)
    else:
        bot.send_message(message.chat.id, "Sorry, I don't need that now.")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    cmd = call.data.split(",")[0]
    owner_id = call.data.split(",")[1]
    product_id = call.data.split(",")[2]
    print(cmd)
    if cmd == "sd":
        if str(call.from_user.id) == str(owner_id):
            db.update_product_status(product_id, 2)
            bot.answer_callback_query(call.id, "Product has been updated to sold")
        else:
            bot.answer_callback_query(call.id, "Sorry, you can't modify this product." )

    elif cmd == "rs":
        if str(call.from_user.id) == str(owner_id):
            db.update_product_status(product_id, 4)
            bot.answer_callback_query(call.id, "Product has been updated to resell")
        else:
            bot.answer_callback_query(call.id, "Sorry, you can't modify this product." )
    elif cmd == "del":
        if str(call.from_user.id) == str(owner_id):
            db.update_product_delete(product_id)
            bot.answer_callback_query(call.id, "Product has been deleted")
        else:
            bot.answer_callback_query(call.id, "Sorry, you can't modify this product." )


def home_state_processor(message, listOfcommands):
    global productForm
    global photos

    if message.text not in listOfcommands:
        bot.send_message(message.chat.id, "Sorry, I don't understand that.")
    elif message.text == "Browse":
        bot.send_message(message.chat.id, "calling the browse function.")
    elif message.text == "Search":
        bot.send_message(message.chat.id, "calling the Search function.")
    elif message.text == "Sell":
        db.update_state(2, message)
        sell_home = cmd.sell(message)
        productForm = {}
        photos = []

    elif message.text == "Your Items":
        db.seller_item(message)
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
        markup.add("Cancel","Finish Sending")
        msgStart = bot.send_message(message.chat.id, """\
    Good:), Now send me some photos of your {0}. Eg. click 📎\
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
    elif message.text == "Cancel":
        bot.send_message(message.chat.id, "Process has been cancelled.")
        db.update_state(8, message)
        send_welcome(message)
    elif message.text == "Finish Sending":
        if len(photos) == 0:
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=2, resize_keyboard=True)
            markup.add("Cancel","Finish Sending")
            msgStart = bot.send_message(message.chat.id, """\
        Plese send me at least one picture. or hit cancel to stop\
        """, reply_markup=markup, parse_mode="html",)

        else:
            db.update_state(6, message) # 6 state is for accepting description
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=2, resize_keyboard=True)
            markup.add("Main Menu","Help")
            msgStart = bot.send_message(message.chat.id, """\
    Please send me product description,

    Eg. Seagate External hard disk
        1TB (Tera byte)
        2 months warranty
\
        """, reply_markup=markup, parse_mode="html",)



def receive_description_state(message, listOfcommands):

    global productForm

    if message.text == "Main Menu":
        bot.send_message(message.chat.id, "You chose to be sent to main menu")
    else:
        productForm["desc"] = message.text

        db.update_state(7, message) # 7 is state for accepting price
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=2, resize_keyboard=True)
        markup.add("Main Menu")
        msgStart = bot.send_message(message.chat.id, """\
Almost there, Set a PRICE for your item. Just a number

Eg. 129, 149.99
\
    """, reply_markup=markup, parse_mode="html",)

def receive_price_state(message, listOfcommands):

    global productForm
    if message.text == "Main Menu":
        bot.send_message(message.chat.id, "You chose to be sent to main menu (price)")
    else:
        productForm["price"] = message.text
        db.update_state(8, message) # 8 is state for accepting location
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=2, resize_keyboard = True)
        button_location = types.KeyboardButton ( text = "Share Location" , request_location = True )
        markup.add(button_location)
        markup.add("Main Menu")
        msgStart = bot.send_message(message.chat.id, """\
One last information, Send me product location. You can enter location or use button below to share

Eg. Around Bole Medhanialem (ቦሌ መዳንያለም አካባቢ)
\
    """, reply_markup=markup, parse_mode="html",)


def receive_location_state(message, listOfcommands):
    global productForm
    global photos
    if message.text == "Main Menu":
        bot.send_message(message.chat.id, "You chose to be sent to main menu (share location)")
    else:
        productForm["location"] = message.text
        print(productForm)
        bot.send_message(message.chat.id, "Done!, Your product has been submitted for approval.")
        db.add_new_product(message, photos, productForm)
        send_welcome(message)



def collect_user_city(message,listOfcommands):
    global userForm
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
