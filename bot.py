from telebot import types
import telebot

TOKEN = "1231860504:AAEx9qZ8znwwdwwq8vOzxskLEGJCBeaSaWs"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=["start"])
def send_welcome(message):
	unique_code = extract_unique_code(message)
	print(unique_code)
	bot.send_message(message.chat.id, """\
Selam {0}, I am here to help you.
You seem new here. Let me help you get started!\
""".format(message.chat.first_name))
