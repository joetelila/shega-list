from telebot import types
import telebot
import datetime
from db_helper import DB_helper
from cmdHelper import commandHelper
from flask import Flask, request
import os


TOKEN = "1231860504:AAEx9qZ8znwwdwwq8vOzxskLEGJCBeaSaWs"
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

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
    print(message.text)
    if extract_unique_code(message.text):
        unique_code = extract_unique_code(message.text).split("_")
        cmd = unique_code[0]
        pro_id = unique_code[1]
        if cmd == "pr":
            print("sending you a detailed inf")
        elif cmd == "wsh":
            print("adding product to your wishlist")
        else:
            bot.send_message(message.chat.id, "Sorry, wrong link")
            send_welcome(message)
    else:
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

def send_welcome_again(message):
    db.update_state(1, message) # state = 1 means the user is at the home page
        #db.sayHello()
    currentTime = datetime.datetime.now()
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=2)
    markup.add("Browse", "Search","Sell","Your Items","Wish Lists","Alert me","Help")
    msgStart = bot.send_message(message.chat.id, """\
    Welcome back, What would you like to do next?\
    """, reply_markup=markup, parse_mode="html",)



def extract_unique_code(text):
    # Extracts the unique_code from the sent /start command.
    return text.split()[1] if len(text.split()) > 1 else None


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
        listOfcommands = ['Electronics','Clothing','Furnitures','Books','Jewelries','Accessories','Watches','Beuty & Health','Others','❌ Cancel']
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
    elif state == 9: # state to browse in home
        listOfcommands = ['Electronics','Clothing','Furnitures','Books','Jewelries','Accessories','Watches','Others','🏠 Home','Next ▶️']
        browse_by_list_state(message, listOfcommands)
    elif state == 10:
        listOfcommands = ['About us','Admin Area','Home']
        help_state(message, listOfcommands)
    elif state == 11:
        listOfcommands = ['Home']
        admin_state(message, listOfcommands)
    elif state == 12:   # collect product title state
        listOfcommands = ['❌ Cancel', 'Skip']
        receive_product_title(message,listOfcommands)
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
Awesome:), The pictures looks nice. Now send me detailed product description.

Example:

Hello, I'm selling my SONY 40" LCD HDTV. Excellent condition and has been well maintained over past few years. I’ve decided to go with a bigger screen for my living room, otherwise I’d keep this TV. It comes with original power cord, remote and stand.

Model # UN55C6400RF

Now, send me yours 😊

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
        bot.answer_callback_query(call.id, "Sorry, you can't modify this product." )
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
        send_welcome_again(message)
    else:
        bot.send_message(message.chat.id, "Sorry, I don't need that now.")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    cmd = call.data.split(",")[0]
    owner_id = call.data.split(",")[1]
    product_id = call.data.split(",")[2]
    if cmd == "sd":
        if str(call.from_user.id) == str(owner_id):
            db.update_product_status(product_id, 2)
            bot.answer_callback_query(call.id, "Product has been updated to sold")
            db.post_sold_item(product_id)
        else:
            bot.answer_callback_query(call.id, "Sorry, you can't modify this product." )
    elif cmd == "rs":
        if str(call.from_user.id) == str(owner_id):
            db.update_product_status_resell(product_id, 0)
            bot.answer_callback_query(call.id, "Product has been re submitted for approval.")
        else:
            bot.answer_callback_query(call.id, "Sorry, you can't modify this product." )
    elif cmd == "del":
        if str(call.from_user.id) == str(owner_id):
            db.update_product_delete(product_id)
            bot.answer_callback_query(call.id, "Product has been deleted")
        else:
            bot.answer_callback_query(call.id, "Sorry, you can't modify this product." )
    elif cmd == "apprv":
        db.update_product_status(product_id, 1)
        bot.answer_callback_query(call.id, "Product has been approved..posting to a channel" )
        db.post_to_channel(product_id)


def home_state_processor(message, listOfcommands):
    global productForm
    global photos

    if message.text not in listOfcommands:
        bot.send_message(message.chat.id, "Sorry, I don't understand that.")
    elif message.text == "Browse":

        cat = "all"

        db.update_state(9, message)
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=3)
        markup.add("Electronics", "Clothing","Furnitures","Books","Jewelries","Accessories","Watches","Others","🏠 Home","Next ▶️")
        msgStart = bot.send_message(message.chat.id, """\
        Use buttons below to filter\
        """, reply_markup=markup, parse_mode="html",)

        db.browse_productS(cat,message)


    elif message.text == "Search":
        bot.send_message(message.chat.id, "Sorry, this feature is under development.")
    elif message.text == "Sell":
        db.update_state(2, message)
        sell_home = cmd.sell(message)
        productForm = {}
        photos = []

    elif message.text == "Your Items":
        db.seller_item(message)
    elif message.text == "Wish Lists":
        bot.send_message(message.chat.id, "Sorry, this feature is under development.")
    elif message.text == "Alert me":
        bot.send_message(message.chat.id, "Sorry, this feature is under development.")
    elif message.text == "Help":
        db.update_state(10, message)
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=2, resize_keyboard=True)
        markup.add("About us", "Admin Area","Home")
        msgStart = bot.send_message(message.chat.id, """\
        Write down help text here\deep
        """, reply_markup=markup, parse_mode="html",)

def selectCategories_state(message,listOfcommands):
    if message.text not in listOfcommands:
        bot.send_message(message.chat.id, "Sorry, I don't understand that.")
    elif message.text == "Electronics":
        select_cat_message(message,message.text)
    elif message.text == "Clothing":
        select_cat_message(message,message.text)
    elif message.text == "Furnitures":
        select_cat_message(message,message.text)
    elif message.text == "Books":
        select_cat_message(message,message.text)
    elif message.text == "Jewelries":
        select_cat_message(message,message.text)
    elif message.text == "Accessories":
        select_cat_message(message,message.text)
    elif message.text == "Watches" :
        select_cat_message(message,message.text)
    elif message.text == "Others" :
        select_cat_message(message,message.text)
    elif message.text == "Beuty & Health" :
        select_cat_message(message,message.text)
    elif message.text == "❌ Cancel" :
        bot.send_message(message.chat.id, "Process has been cancelled")
        send_welcome_again(message)

def select_cat_message(message, message_text):
    productForm["cat"] = message_text
    db.update_state(12, message)
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=2, resize_keyboard=True)
    markup.add("❌ Cancel", "Skip")
    msgStart = bot.send_message(message.chat.id, """\
Good:), Now send me Product title.

Eg. SONY Television 40" TV \
""".format(message.text.lower()), reply_markup=markup, parse_mode="html",)


def receive_product_title(message, listOfcommands):
    global productForm
    if message.text == "❌ Cancel":
        bot.send_message(message.chat.id, "process has been cancelled")
        send_welcome(message)
    elif message.text == "Skip":
        bot.send_message(message.chat.id, "You have skipped product title. Make sure to include it in your product description.")
        productForm["title"] = "empty"
        db.update_state(5, message)
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=2, resize_keyboard=True)
        markup.add("Cancel","Finish Sending")
        msgStart = bot.send_message(message.chat.id, """\
Nice:), Now send me some photos of your product.
Eg. click 📎\
""", reply_markup=markup, parse_mode="html",)

    else:
        productForm["title"] = message.text
        db.update_state(5, message)
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=2, resize_keyboard=True)
        markup.add("Cancel","Finish Sending")
        msgStart = bot.send_message(message.chat.id, """\
Nice:), Now send me some photos of your product. Eg. click 📎\
""", reply_markup=markup, parse_mode="html",)


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
Awesome:), The pictures looks nice. Now send me detailed product description.

Example:

Hello, I'm selling my SONY 40" LCD HDTV. Excellent condition and has been well maintained over past few years. I’ve decided to go with a bigger screen for my living room, otherwise I’d keep this TV. It comes with original power cord, remote and stand.

Model # UN55C6400RF

Now, send me yours 😊

\
        """, reply_markup=markup, parse_mode="html",)



def receive_description_state(message, listOfcommands):

    global productForm

    if message.text == "Main Menu":
        bot.send_message(message.chat.id, "sending you to main menu.")
        send_welcome_again(message)
    elif message.text == "Help":
        bot.send_message(message.chat.id, "Sorry, we are finishing the help menu.")
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
        send_welcome_again(message)
    else:
        productForm["location"] = message.text
        print(productForm)
        bot.send_message(message.chat.id, "Done!, Your product has been submitted for approval.")
        db.add_new_product(message, photos, productForm)
        send_welcome_again(message)

def browse_by_list_state(message, listOfcommands):

    if message.text not in listOfcommands:
        bot.send_message(message.chat.id, "Sorry, I don't understand that.")
    elif message.text == "Electronics":
        db.browse_productS(message.text,message)
    elif message.text == "Clothing":
        db.browse_productS(message.text,message)
    elif message.text == "Furnitures":
        db.browse_productS(message.text,message)
    elif message.text == "Books":
        db.browse_productS(message.text,message)
    elif message.text == "Jewelries":
        db.browse_productS(message.text,message)
    elif message.text == "Accessories":
        db.browse_productS(message.text,message)
    elif message.text == "Watches" :
        db.browse_productS(message.text,message)
    elif message.text == "Others" :
        db.browse_productS(message.text,message)
    elif message.text == "🏠 Home" :
        bot.send_message(message.chat.id, "Sending you to home")
        send_welcome_again(message)
    elif message.text == "Next ▶️" :
        db.browse_next_products(message.text,message)

def help_state(message, listOfcommands):

    if message.text in listOfcommands:
        if message.text == "About us":
            bot.send_message(message.chat.id, "Will update soon.")
        elif message.text == "Admin Area":

            if db.isAdmin(message):
                db.update_state(11, message) # 7 is state for accepting price
                markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=2, resize_keyboard=True)
                markup.add("Home")
                msgStart = bot.send_message(message.chat.id, """Sending you all UNAPPROVED items . . .""", reply_markup=markup, parse_mode="html",)
                db.un_approved_items(message)
            else:
                bot.send_message(message.chat.id, "Sorry, you're not allowed to use this button.")
                send_welcome(message)

        elif message.text == "Home":
            send_welcome(message)
    else:
        bot.send_message(message.chat.id, "Sorry, I don't understand that.")


    message.text

def admin_state(message, listOfcommands):
    if message.text  in listOfcommands:
        if message.text == "Home":
            send_welcome(message)
    else:
        bot.send_message(message.chat.id, "Sorry, I don't understand that.")



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



@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://shegalist.herokuapp.com/' + TOKEN)
    return "!", 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
