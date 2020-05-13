import sqlite3

#define connection

class DB_helper:
    def __init__(self, bot, dbname = "shegalist.db"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.bot = bot
    def create_userTable(self):
        command1 = """CREATE TABLE IF NOT EXISTS
        users(user_ID INTEGER PRIMARY KEY, tgID TEXT, fName TEXT, lName TEXT,
        phoneNumber TEXT , city TEXT, subcityOrkeb TEXT, state INTEGER )"""
        self.cursor.execute(command1)
    def sayHello(self):
        print("Hello from dh helper")

    def isUserRegistered(self, message):
        # check if the user is already registered
        command_checkuser = "SELECT * FROM users WHERE tgID = "+str(message.from_user.id)
        result = self.cursor.execute(command_checkuser)
        if self.cursor.fetchone() is None:
            return False
        else:
            return True
