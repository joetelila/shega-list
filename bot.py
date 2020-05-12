from telebot import types
import telebot
import datetime

TOKEN = "1231860504:AAEx9qZ8znwwdwwq8vOzxskLEGJCBeaSaWs"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=["start"])
def send_welcome(message):
    currentTime = datetime.datetime.now()
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=2)
    markup.add("Browse", "Search","Sell","Your Items","Wish Lists","Alert Me","Help")
    bot.send_message(message.chat.id, """\
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

def extract_unique_code(text):
	# extracts unique code for the sent or start commands
	return text.chat.id

bot.polling()
