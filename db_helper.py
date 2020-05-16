import sqlite3
import threading
import telebot
from cmdHelper import commandHelper
import time
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
#define connection

lock = threading.Lock()




class DB_helper:
    def __init__(self, bot, dbname = "shegalist.db"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.bot = bot

    def create_userTable(self):
        command1 = """CREATE TABLE IF NOT EXISTS
        users(tgID BIGINT PRIMARY KEY, fName TEXT, lName TEXT,
        phoneNumber TEXT , city TEXT, state INTEGER, registered INTEGER )"""
        self.cursor.execute(command1)
        self.conn.commit()
    def create_productTable(self):
        command1 = """CREATE TABLE IF NOT EXISTS
        products(productID INTEGER PRIMARY KEY AUTOINCREMENT, userID BIGINT, cat TEXT, pictures TEXT, description TEXT,
        price TEXT , location TEXT, status INTEGER )"""
        self.cursor.execute(command1)
        self.conn.commit()

    def saveuser(self, message):
        tgId = message.from_user.id
        fname = message.from_user.first_name
        lname = message.from_user.last_name
        registered = 0
        state = 1
        if not self.isUserNew(message):
            self.cursor.execute("""INSERT INTO users ('tgID', 'fName','lName','state','registered') VALUES (?, ?, ?, ?, ?)""", (tgId, str(fname),str(lname), state, registered))
            self.conn.commit()

    def isUserNew(self, message):
        # check if the user is already registered
        command_checkuser = "SELECT * FROM users WHERE tgID = "+str(message.from_user.id)
        result = self.cursor.execute(command_checkuser)
        if len(result.fetchall()) == 0:
            return False
        else:
            return True

    def isUserRegistered(self, message):
        # check if the user is already registered
        command_checkuser = "SELECT * FROM users WHERE tgID = "+str(message.from_user.id)
        result = self.cursor.execute(command_checkuser)
        users = result.fetchall()
        if len(users) == 1 and users[0][6] == 1:
            print("registered")
            return True
        else:
            print("not registered")
            return False

    def register_user(self, userData,message):
        phone = userData["phone"]
        city = userData["city"]
        registered = 1
        self.cursor.execute("""UPDATE  users SET
            phoneNumber = ?,
            city = ?,
            registered = ?
            WHERE tgID = ?""",(str(phone),str(city), registered,str(message.from_user.id)))
        self.conn.commit()
        self.bot.send_message(message.chat.id, "Sweet;), Successfully registered")

    def update_state(self, state, message):
        self.cursor.execute("""UPDATE  users SET
            state = ?
            WHERE tgID = ?
                """,(state,str(message.from_user.id)))
        self.conn.commit()

    def get_user_state(self,message):
        lock.acquire(True)
        command_checkuser = "SELECT state FROM users WHERE tgID = "+str(message.from_user.id)
        result = self.cursor.execute(command_checkuser)
        state = result.fetchall()
        lock.release()
        return state[0][0]

    def add_new_product(self, message, photos, productForm):

        location = productForm["location"]
        status = 0 # unaproved
        separator = ","
        self.cursor.execute("""INSERT INTO products ('userID', 'cat','pictures','description','price','location','status') VALUES (?, ?, ?, ?, ?, ?,?)""", (message.from_user.id,str(productForm["cat"]), separator.join(map(str,photos)),productForm["desc"], productForm["price"],location, status))
        self.conn.commit()
    def seller_item(self, message):
        self.send_typing(message)
        self.bot.send_chat_action(message.chat.id, 'typing')
        lock.acquire(True)
        command_checkuser = "SELECT * FROM products WHERE userID = "+str(message.from_user.id)
        result = self.cursor.execute(command_checkuser)
        products = result.fetchall()
        lock.release()


        for i in products:
            status = i[7]
            price = i[5]
            desc = i[4]
            owner_id = i[1]  # I need this id to make pass to the inline buttons
            pro_id = i[0]
            buttonid = ""+str(owner_id)+","+str(pro_id)


            if status == 0:
                status = "APPROVAL_PENDING"
            elif status == 1:
                status = "APPROVED"
            elif status == 2:
                status = "SOLD"
            elif status == 3:
                status = "UNAPPROVED"
            elif status == 4:
                status = "RESELLING"
            else:
                status ="UNLISTED"

            picture = i[3].split(",")
            file_id1 = picture[1]
            file1 = self.bot.get_file(file_id1)
            file1 = self.bot.download_file(file1.file_path)
            with open("file1.png","wb") as f:
                f.write(file1)
            self.bot.send_photo(message.chat.id, file1, caption ="""
#{0}

{1}

PRICE : {2} Br
            """.format(status,desc,price) ,reply_markup=self.gen_markup(buttonid,status)) # status parameter is to change the sold/resell button

    def send_typing(self,message):
        self.bot.send_chat_action(message.chat.id, 'typing')
        time.sleep(2)

    def gen_markup(self,id,status):

        print(status)

        markup = InlineKeyboardMarkup()
        callback_btn_detail = InlineKeyboardButton(text="🌟 Detail", callback_data="det,{0}".format(id))
        if str(status) == "SOLD":
            callback_sold = InlineKeyboardButton(text="🔄 Resell", callback_data="rs,{0}".format(id))
        else:
            callback_sold = InlineKeyboardButton(text="✅ Sold", callback_data="sd,{0}".format(id))
        callback_btn_edit = InlineKeyboardButton(text="✏️ Edit", callback_data="ed,{0}".format(id))
        callback_btn_delete = InlineKeyboardButton(text="❌ Delete", callback_data="del,{0}".format(id))
        markup.row_width = 2
        markup.add(callback_btn_detail, callback_sold, callback_btn_edit, callback_btn_delete)

        return markup

    def update_product_status(self, id, data):
        self.cursor.execute("""UPDATE  products SET
            status = ?
            WHERE productID = ?
                """,(data,id))
        self.conn.commit()

    def update_product_delete(self, id):
        self.cursor.execute("""DELETE FROM products
            WHERE productID = ?
                """,(id))
        self.conn.commit()
