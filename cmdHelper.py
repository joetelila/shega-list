from telebot import types
import time

class commandHelper:
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db

    def sell(self, message):
        #self.bot.send_message(message.chat.id, "calling the sell function.")
        result = self.db.isUserRegistered(message)
        if not result:  # if the user is not registered
            self.bot.send_message(message.chat.id, "{0} ;), I see it's your first time selling here. Let me register you first.".format(message.chat.first_name),)
            self.register(message)
        else:
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=3, resize_keyboard = True)
            markup.add("Electronics", "Clothing","Furnitures","Books","Jewelries","Accessories","Watches","Beuty & Health","Others",'❌ Cancel')
            msgStart = self.bot.send_message(message.chat.id, """\
        Perfect:), What would you like to sell??\
        """, reply_markup=markup, parse_mode="html",)
            self.db.update_state(4, message)

    def send_typing(self,message):
        self.bot.send_chat_action(message.chat.id, 'typing')
        time.sleep(2)

    def register(self, message):
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=1, resize_keyboard = True)
        markup.add("Back")
        msgStart = self.bot.send_message(message.chat.id, """\
    Send me your city. Eg: Addis Ababa\
    """, reply_markup=markup, parse_mode="html",)

    def accept_user_number(self, message):
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=3, resize_keyboard = True)
        button_phone = types.KeyboardButton (text = "Share Number" , request_contact = True )
        markup.add(button_phone)
        markup.add("Main Menu","Skip")
        msgStart = self.bot.send_message(message.chat.id, """\
    Click the button below to share your contact. Your contact is only used for a buyer to contact you.\
    """, reply_markup=markup, parse_mode="html")
