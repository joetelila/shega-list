import sqlite3
import threading
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
        products(productID INTEGER PRIMARY KEY AUTOINCREMENT, userID BIGINT, cat INT, pictures TEXT, description TEXT,
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
