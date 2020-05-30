from cmdHelper import commandHelper
import time
import re # regexp matching library
# telegram library imports
import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
# firebase realtime db imports
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db



#define connection
db_limit = 5
db_offset = 0
total_pro = 0
category = "all"

class DB_helper:
    def __init__(self, bot):
        self.bot = bot
        cred = credentials.Certificate("creds/shega-list-firebase.json")
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://shega-list.firebaseio.com/'
        })
        self.user_ref = db.reference("users")
        self.product_ref = db.reference("products")

    def saveuser(self, message):
        tgId = message.from_user.id
        fname = message.from_user.first_name
        lname = message.from_user.last_name
        registered = 0
        state = 1
        if not self.isUserNew(message):
            self.user_ref.push({
            'tgId' : tgId,
            'fname': fname,
            'lname': lname,
            'state': state,
            'registered': registered
            })


    def isUserNew(self, message):
        # check if the user is already registered
        result = self.user_ref.order_by_child('tgId').equal_to(message.from_user.id).get()
        if len(result) == 1:
            return True
        else:
            return False

    def isUserRegistered(self, message):
        # check if the user is already registered

        result = self.user_ref.order_by_child('tgId').equal_to(message.from_user.id).get()
        for key, val in result.items():
            values = val

        if len(result) == 1 and val["registered"] == 1:
            print("registered")
            return True
        else:
            print("user not registered")
            return False


    def isAdmin(self, message):  # ->

        result = self.user_ref.order_by_child('tgId').equal_to(message.from_user.id).get()
        for key, val in result.items():
            values = val

        if len(result) == 1 and val["privilage"] == 1:
            print("admin")
            return True
        else:
            print("not admin")
            return False



    def register_user(self, userData,message): #  ->
        phone = userData["phone"]
        city = userData["city"]
        registered = 1
        privilage = 0

        result = self.user_ref.order_by_child('tgId').equal_to(message.from_user.id).get()
        for key, val in result.items():
            user_key = key
        user_ref = self.user_ref.child(user_key)
        user_ref.update({
            'phoneNumber': phone,
            'city': city,
            'registered': registered,
            'privilage': privilage
        })
        self.bot.send_message(message.chat.id, "Sweet;), Successfully registered")


        '''lock.acquire(True)
        self.cursor.execute("""UPDATE  users SET
            phoneNumber = ?,
            city = ?,
            registered = ?,
            privilage = ?
            WHERE tgID = ?""",(str(phone),str(city), registered,privilage,str(message.from_user.id)))
        self.conn.commit()
        lock.release()
        self.bot.send_message(message.chat.id, "Sweet;), Successfully registered")'''

    def update_state(self, state, message): # -> done

        result = self.user_ref.order_by_child('tgId').equal_to(message.from_user.id).get()
        for key, val in result.items():
            user_key = key
        user_ref = self.user_ref.child(user_key)
        user_ref.update({
            'state': state
        })

    def get_user_state(self,message):  # -> done

        result = self.user_ref.order_by_child('tgId').equal_to(message.from_user.id).get()
        for key, val in result.items():
            val = val
        return val['state']

        '''lock.acquire(True)
        command_checkuser = "SELECT state FROM users WHERE tgID = "+str(message.from_user.id)
        result = self.cursor.execute(command_checkuser)
        state = result.fetchall()
        lock.release()
        return state[0][0] '''

    def add_new_product(self, message, photos, productForm): # ->
        user_detail = self.user_ref.order_by_child('tgId').equal_to(message.from_user.id).get()
        for key, val in user_detail.items():
            user = val
        location = productForm["location"]
        status = 0 # unaproved
        separator = ","
        deleted = 0
        soldPost = 0
        self.product_ref.push({
                'userID' : message.from_user.id,
                'cat': productForm["cat"],
                'pictures': separator.join(map(str,photos)),
                'title': productForm["title"],
                'description': productForm["desc"],
                'price': productForm["price"],
                'location': location,
                'status': status,
                'deleted': deleted,
                'soldPost': soldPost,
                'message_id':message.chat.id,
                'seller_name': user["fname"]
                })
        self.bot.send_message(565126182, "Hey Joe, someone just added a new product. Please approve fast.")
        self.bot.send_message(966205634, "Hey Shega, someone just added a new product. Please approve fast.")


    def seller_item(self, message):  # ->
        self.bot.send_chat_action(message.chat.id, 'typing')
        products = []
        result = self.product_ref.order_by_child('userID').equal_to(message.from_user.id).get() # where status = 0, means unapproved
        for key, val in result.items():
            val["key"] = key
            if val["deleted"] == 0:
                products.append(val)
            else:
                pass

        if len(products) == 0:
            self.bot.send_message(message.chat.id, "Apperently, your list is empty.")
        else:
            for i in products:
                print(i)
                status = i["status"]
                price = i["price"]
                desc = i["description"]
                owner_id = i["userID"]  # I need this id to make pass to the inline buttons
                pro_id = i["key"]
                title = i["title"]
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

                picture = i["pictures"].split(",")
                file_id1 = picture[1]
                file1 = self.bot.get_file(file_id1)
                file1 = self.bot.download_file(file1.file_path)
                with open("file1.png","wb") as f:
                    f.write(file1)
                self.bot.send_photo(message.chat.id, file1, caption ="""
#{0}   @shegalist

{3}

{1}

PRICE : {2} Br
                """.format(status,desc,price,title) ,reply_markup=self.gen_markup(buttonid,status)) # status parameter is to change the sold/resell button

    def send_typing(self,message):
        self.bot.send_chat_action(message.chat.id, 'typing')
        time.sleep(2)

    def gen_markup(self,id,status):
        markup = InlineKeyboardMarkup()
        callback_btn_detail = InlineKeyboardButton(text="🔅 Detail", url="https://telegram.me/shegalistbot?start=pr_joe_shega_{0}".format(id.split(",")[1]))
        if str(status) == "SOLD":
            callback_sold = InlineKeyboardButton(text="🔄 Resell", callback_data="rs,{0}".format(id))
        else:
            callback_sold = InlineKeyboardButton(text="✅ Sold", callback_data="sd,{0}".format(id))
        callback_btn_edit = InlineKeyboardButton(text="✏️ Edit", callback_data="ed,{0}".format(id))
        callback_btn_delete = InlineKeyboardButton(text="❌ Delete", callback_data="del,{0}".format(id))
        markup.row_width = 2
        markup.add(callback_btn_detail, callback_sold, callback_btn_edit, callback_btn_delete)
        return markup

    def browse_productS(self, cat,message):

        global db_limit
        global db_offset
        global total_pro
        global category

        db_limit = 5
        db_offset = 0
        total_pro = self.get_total_product(cat)

        if cat == category:
            lock.acquire(True)
            result = self.cursor.execute("""SELECT * FROM  products WHERE
                status = ?
                AND deleted = ?
                    """,(1,0))
            lock.release()
            products = result.fetchall()
            self.send_products(products,message)
            print(len(products))

        else:
            category = cat
            lock.acquire(True)
            result = self.cursor.execute("""SELECT * FROM  products WHERE
                    cat = ?
                    AND status = ?
                    AND deleted = ?
                        """,(cat,1,0))  # deleted false
            lock.release()
            products = result.fetchall()
            self.send_products(products,message)


    def un_approved_items(self, message):

        products = []
        result = self.product_ref.order_by_child('status').equal_to(0).get() # where status = 0, means unapproved
        for key, val in result.items():
            val["key"] = key
            if val["deleted"] == 0:
                products.append(val)
            else:
                pass
        self.send_unapproved_products(products,message)




    def browse_next_products(self,cat, message):

        global db_offset
        global db_limit
        global category

        if category == "all":
            self.bot.send_message(message.chat.id, "sending you a next of all")
        else:
            self.bot.send_message(message.chat.id, "sending you a next of {0}".format(category))


        db_offset = db_offset + db_limit

        print(db_limit, db_offset)


    def get_total_product(self, cat):
        if cat == category:
            lock.acquire(True)
            result = self.cursor.execute("""SELECT * FROM  products WHERE
                status = ?
                AND deleted = ?
                    """,(1,0))
            products = result.fetchall()
            lock.release()
            return len(products)
        else:
            lock.acquire(True)
            result = self.cursor.execute("""SELECT * FROM  products WHERE
                    cat = ?
                    AND status = ?
                    AND deleted = ?
                        """,(cat,1,0))  # deleted false
            products = result.fetchall()
            lock.release()
            return len(products)

    def send_unapproved_products(self, products,message):
        if len(products) >= 1:
            for pros in products:
                self.send_unapproved_Images(pros,message)
        else:
            self.bot.send_message(message.chat.id, "Sorry, empty list.")



    def send_products(self, products,message):
        if len(products) >= 1:
            for pros in products:
                self.sendImages(pros,message)
        else:
            self.bot.send_message(message.chat.id, "Sorry, empty list.")


    def sendImages(self, products,message):

        self.send_typing(message)
        pictures = products[3].split(",")
        file_id1 = pictures[0]
        file1 = self.bot.get_file(file_id1)
        file1 = self.bot.download_file(file1.file_path)
        with open("file1.png","wb") as f:
            f.write(file1)
        self.bot.send_photo(message.chat.id, file1, caption ="""
#{0}   @shegalist

{4}

{1}

Price : {2} Br | Contact : {3}
        """.format(products[2],products[4],products[5],self.get_mention(message),products[9]) ,reply_markup=self.gen_markup_post(products[0]), parse_mode="Markdown") # status parameter is to change the sold/resell button

    def send_unapproved_Images(self, products,message):

        self.send_typing(message)
        pictures = products["pictures"].split(",")
        file_id1 = pictures[0]
        file1 = self.bot.get_file(file_id1)
        file1 = self.bot.download_file(file1.file_path)
        with open("file1.png","wb") as f:
            f.write(file1)
        self.bot.send_photo(message.chat.id, file1, caption ="""
#{0}   @shegalist

{5}

{1}

Price: {2}Br | Contact: {3}

📍: {4}
        """.format(products["cat"],products["description"],products["price"],self.get_mention(message),products["location"], products["title"]) ,reply_markup=self.gen_markup_unapproved(products["key"],message.chat.id), parse_mode="Markdown") # status parameter is to change the sold/resell button


    def gen_markup_unapproved(self,id,user_id):

        markup = InlineKeyboardMarkup()
        callback_btn_detail = InlineKeyboardButton(text="🔅 Detail", url="https://telegram.me/shegalistbot?start=pr_joe_shega_{0}".format(id))
        callback_btn_buy = InlineKeyboardButton(text="❌ Decline", callback_data="decline,{0},{1}".format(user_id,id))
        callback_btn_wishlist = InlineKeyboardButton(text="✅ Approve", callback_data="apprv,{0},{1}".format(user_id,id))
        markup.row_width = 3
        markup.add(callback_btn_detail, callback_btn_buy, callback_btn_wishlist)

        return markup


    def update_product_status(self, id, data): # ->

        pro_ref = self.product_ref.child(id)
        pro_ref.update({
            'status': data
            })

        product = self.product_ref.child(id).get()
        if data == 1:
            self.bot.send_message(product["message_id"], "Hey {0}, your product has been approved 🤗.".format(product["seller_name"]))
        elif data == 3:
            self.bot.send_message(product["message_id"], "Hey {0}, Sorry 😔 , we have to disapprove your product. Please refer to our guidline in the help section. Contact us @shega_support if you need help.".format(product["seller_name"]))





    def update_product_status_resell(self, id, data):  # this method resets the sold post aswell


        pro_ref = self.product_ref.child(id)
        pro_ref.update({
            'status': data,
            'soldPost':0
            })

        '''lock.acquire(True)
        self.cursor.execute("""UPDATE  products SET
            status = ?,
            soldPost = ?
            WHERE productID = ?
                """,(data,0,id))
        self.conn.commit()
        lock.release() '''


    def post_sold_item(self,id):

        product = self.product_ref.child(id).get()
        product["key"] = id

        if product["status"] == 0:
            return 1
        elif product["status"] == 1:
            if product["soldPost"] == 1:
                print("This product is already sold")
                return 2
            else:
                msgStart = self.bot.send_message("@shegalist", """
    ------SOLD OUT-------
#{0}   @shegalist

{1}

{2}

Price: {3} Br

Have anything to sell?🤔. Post it on @shegalistbot
    -------SOLD OUT--------
            """.format(product["cat"],product["title"],product["description"],product["price"]))
                self.update_sold_post_status(id)

    def update_sold_post_status(self,id):

        pro_ref = self.product_ref.child(id)
        data = 1
        pro_ref.update({
            'soldPost': data
            })


    def post_to_channel(self,product_id):
        # self.bot.send_message("@shegalist","Hi")
        product = self.product_ref.child(product_id).get()
        product["key"] = product_id
        user_ID = product["userID"]
        self.post_image_to_channel(product, user_ID)


        '''lock.acquire(True)
        result = self.cursor.execute("""SELECT * FROM  products WHERE
            productID = ?
            AND deleted = ?
                """,(product_id,0))
        products = result.fetchall()
        lock.release()

        if len(products) == 1:
            user_ID = products[0][1]
            self.post_image_to_channel(products, user_ID)
        else:
            print("something went wrong..at post to a channel method") '''

    def post_image_to_channel(self, products, user_ID):
        pictures = products["pictures"].split(",")
        if len(pictures) == 1:
            self.post_one_images("@shegalist",pictures,products,user_ID)
        elif len(pictures) == 2:
            self.post_two_images("@shegalist",pictures,products,user_ID)
        elif len(pictures) == 3:
            self.post_three_images("@shegalist",pictures,products,user_ID)
        else:
            print("something went wrong..at post to a post_image_to_channel method")
            return
        if self.isGPS(products):
            self.send_location_and_buttons("@shegalist", products)

    def send_location_and_buttons(self, id, product):

        location = product["location"]
        location = location.split(",")
        longi = location[0]
        latit = location[1]
        self.bot.send_location(id, latitude=latit,longitude=longi, reply_markup=self.gen_markup_post(product["key"]) ) # status parameter is to change the sold/resell button


    def isGPS(self, product):
        location = product["location"]
        isgps = re.match("^[-+]?([1-8]?\d(\.\d+)?|90(\.0+)?),\s*[-+]?(180(\.0+)?|((1[0-7]\d)|([1-9]?\d))(\.\d+)?)$", location)
        if isgps:
            return True
        else:
            return False

    def post_one_images(self, id, images, products,user_ID):

        file_id1 = images[0]
        file1 = self.bot.get_file(file_id1)
        file1 = self.bot.download_file(file1.file_path)
        result = self.user_ref.order_by_child('tgId').equal_to(user_ID).get()
        for key, val in result.items():
            user_det = val

        with open("file1.png","wb") as f:
            f.write(file1)

        if self.isGPS(products):
            if products["title"] == "empty":
                photo1 = telebot.types.InputMediaPhoto(open("file1.png","rb"), caption="""
#{0}   @shegalist

{1}

Price: {2}Br | Contact: {3}

📍: {4}, use map below for exact location.

Have anything to sell?🤔. Post it on @shegalistbot
            """.format(products["cat"],products["description"],products["price"],self.get_post_mention(user_ID), user_det["city"] ), parse_mode="Markdown")
            else:
                photo1 = telebot.types.InputMediaPhoto(open("file1.png","rb"), caption="""
#{0}   @shegalist

{4}

{1}

Price: {2}Br | Contact: {3}

📍: {5}, use map below for exact location.

Have anything to sell?🤔. Post it on @shegalistbot
            """.format(products["cat"],products["description"],products["price"],self.get_post_mention(user_ID),products["title"], user_det["city"]), parse_mode="Markdown")


        else:
            if products["title"] == "empty":
                photo1 = telebot.types.InputMediaPhoto(open("file1.png","rb"), caption="""
#{0}   @shegalist

{1}

Price: {2}Br | Contact: {3}

📍: {4}, {5}

Have anything to sell?🤔. Post it on @shegalistbot
            """.format(products["cat"],products["description"],products["price"],self.get_post_mention(user_ID),products["location"], user_det["city"]), parse_mode="Markdown")
            else:
                photo1 = telebot.types.InputMediaPhoto(open("file1.png","rb"), caption="""
#{0}   @shegalist

{5}

{1}

Price: {2}Br | Contact: {3}

📍: {4}, {6}

Have anything to sell?🤔. Post it on @shegalistbot
        """.format(products["cat"],products["description"],products["price"],self.get_post_mention(user_ID),products["location"],products["title"], user_det["city"]), parse_mode="Markdown")



        media = [photo1]
        self.bot.send_media_group(id, media)

    def post_two_images(self, id, images, products,user_ID):

        file_id1 = images[0]
        file_id2 = images[1]
        file1 = self.bot.get_file(file_id1)
        file1 = self.bot.download_file(file1.file_path)
        file2 = self.bot.get_file(file_id2)
        file2 = self.bot.download_file(file2.file_path)
        result = self.user_ref.order_by_child('tgId').equal_to(user_ID).get()
        for key, val in result.items():
            user_det = val

        with open("file1.png","wb") as f:
            f.write(file1)
        with open("file2.png","wb") as f:
            f.write(file2)

        photo1 = telebot.types.InputMediaPhoto(open("file1.png","rb"))

        if self.isGPS(products):
            if products["title"] == "empty":
                photo2 = telebot.types.InputMediaPhoto(open("file2.png","rb"), caption="""
#{0}   @shegalist

{1}

Price: {2}Br | Contact: {3}

📍: {4}, use map below for exact location.

Have anything to sell?🤔. Post it on @shegalistbot
            """.format(products["cat"],products["description"],products["price"],self.get_post_mention(user_ID), user_det["city"]), parse_mode="Markdown")
            else:
                photo2 = telebot.types.InputMediaPhoto(open("file2.png","rb"), caption="""
#{0}   @shegalist

{4}

{1}

Price: {2}Br | Contact: {3}

📍: {5}, use map below for exact location.

Have anything to sell?🤔. Post it on @shegalistbot
            """.format(products["cat"],products["description"],products["price"],self.get_post_mention(user_ID),products["title"], user_det["city"]), parse_mode="Markdown")

        else:
            if products["title"] == "empty":
                photo2 = telebot.types.InputMediaPhoto(open("file2.png","rb"), caption="""
#{0}   @shegalist

{1}

Price: {2}Br | Contact: {3}

📍: {4}, {5}

Have anything to sell?🤔. Post it on @shegalistbot
            """.format(products["cat"],products["description"],products["price"],self.get_post_mention(user_ID),products["location"], user_det["city"]), parse_mode="Markdown")
            else:
                photo2 = telebot.types.InputMediaPhoto(open("file2.png","rb"), caption="""
#{0}   @shegalist

{5}

{1}

Price: {2}Br | Contact: {3}

📍: {4}, {6}

Have anything to sell?🤔. Post it on @shegalistbot
            """.format(products["cat"],products["description"],products["price"],self.get_post_mention(user_ID),products["location"],products["title"], user_det["city"]), parse_mode="Markdown")





        media = [photo1, photo2]
        self.bot.send_media_group(id, media)

    def post_three_images(self, id, images, products,user_ID):

        file_id1 = images[0]
        file_id2 = images[1]
        file_id3 = images[2]
        file1 = self.bot.get_file(file_id1)
        file1 = self.bot.download_file(file1.file_path)
        file2 = self.bot.get_file(file_id2)
        file2 = self.bot.download_file(file2.file_path)
        file3 = self.bot.get_file(file_id3)
        file3 = self.bot.download_file(file3.file_path)

        result = self.user_ref.order_by_child('tgId').equal_to(user_ID).get()
        for key, val in result.items():
            user_det = val
        #
        with open("file1.png","wb") as f:
            f.write(file1)
        with open("file2.png","wb") as f:
            f.write(file2)
        with open("file3.png","wb") as f:
            f.write(file3)

        photo2 = telebot.types.InputMediaPhoto(open("file2.png","rb"))
        photo3 = telebot.types.InputMediaPhoto(open("file3.png","rb"))

        if self.isGPS(products):
            if products["title"] == "empty":
                photo1 = telebot.types.InputMediaPhoto(open("file1.png","rb"), caption="""
#{0}   @shegalist

{1}

Price: {2}Br | Contact: {3}

📍: {4}, use map below for exact location.

Have anything to sell?🤔. Post it on @shegalistbot
            """.format(products["cat"],products["description"],products["price"],self.get_post_mention(user_ID), user_det["city"]), parse_mode="Markdown")
            else:
                photo1 = telebot.types.InputMediaPhoto(open("file1.png","rb"), caption="""
#{0}   @shegalist

{4}

{1}

Price: {2}Br | Contact: {3}

📍: {5}, use map below for exact location

Have anything to sell?🤔. Post it on @shegalistbot
            """.format(products["cat"],products["description"],products["price"],self.get_post_mention(user_ID),products["title"], user_det["city"]), parse_mode="Markdown")



        else:
            if products["title"] == "empty":
                photo1 = telebot.types.InputMediaPhoto(open("file1.png","rb"), caption="""
#{0}   @shegalist

{1}

Price: {2}Br | Contact: {3}

📍: {4}, {5}

Have anything to sell?🤔. Post it on @shegalistbot
            """.format(products["cat"],products["description"],products["price"],self.get_post_mention(user_ID),products["location"], user_det["city"]), parse_mode="Markdown")
            else:
                photo1 = telebot.types.InputMediaPhoto(open("file1.png","rb"), caption="""
#{0}   @shegalist

{5}

{1}

Price: {2}Br | Contact: {3}

📍: {4}, {6}

Have anything to sell?🤔. Post it on @shegalistbot
            """.format(products["cat"],products["description"],products["price"],self.get_post_mention(user_ID),products["location"],products["title"],user_det["city"]), parse_mode="Markdown")



        media = [photo1, photo2,photo3]
        self.bot.send_media_group(id, media)


    def gen_markup_post(self,id):
        markup = InlineKeyboardMarkup()
        callback_btn_buy = InlineKeyboardButton(text="🔅 Detail", url="https://telegram.me/shegalistbot?start=pr_joe_shega_{0}".format(id))
        callback_btn_wishlist = InlineKeyboardButton(text="❤️ Add to wishlist", url="https://telegram.me/shegalistbot?start=wsh_joe_shega_{0}".format(id))
        markup.row_width = 2
        markup.add(callback_btn_buy, callback_btn_wishlist)

        return markup


    def update_product_delete(self, id):

        deleted = 1

        user_ref = self.product_ref.child(id)
        user_ref.update({
            'deleted': deleted
        })

        '''lock.acquire(True)
        self.cursor.execute("""DELETE FROM products
            WHERE productID = ?
                """,(id))
        self.conn.commit()
        lock.release()'''

    def get_mention(self, message):
        user_id = message.from_user.id
        user_name = message.from_user.first_name
        mention = "["+user_name+"](tg://user?id="+str(user_id)+")"
        return mention

    def get_post_mention(self, userID):
        user_id = userID
        user_name = "Seller"
        mention = "["+user_name+"](tg://user?id="+str(user_id)+")"
        return mention

    def send_detailed_pro_info(self, product_id, message):
        product = self.product_ref.child(product_id).get()
        product["key"] = product_id
        pictures = product["pictures"].split(",")
        user_ID = product["userID"]
        if len(pictures) == 1:
            self.post_one_images(message.chat.id,pictures,product,user_ID)
        elif len(pictures) == 2:
            self.post_two_images(message.chat.id,pictures,product,user_ID)
        elif len(pictures) == 3:
            self.post_three_images(message.chat.id,pictures,product,user_ID)
        else:
            print("something went wrong..at post to a post_image_to_channel method")
            return
        if self.isGPS(product):
            self.send_location_and_buttons(message.chat.id,product)
