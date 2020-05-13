from telebot import types

class commandHelper:
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db
    def sell(self, message):
        #self.bot.send_message(message.chat.id, "calling the sell function.")
        result = self.db.isUserRegistered(message)
        if result:  # if the user is registered
            print("send me you item detail")
        else:
            self.bot.send_message(message.chat.id, "Dani ;), I see it's your first time selling here.")
            self.register(message)

    def register(self, message):
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=1, resize_keyboard = True)
        markup.add("<- Back","Main Menu")
        msgStart = self.bot.send_message(message.chat.id, """\
    Send me your city. Eg: Addis Ababa\
    """, reply_markup=markup, parse_mode="html",)
