#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import webapp2
import jinja2
import time
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates/')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)


class Items3(db.Model):
    ItemName = db.StringProperty(required = True)
    phone = db.IntegerProperty(required = True)
    email = db.StringProperty(required = True)
    isNeed = db.BooleanProperty(required = True)
    isCompleted = db.BooleanProperty(required = True)
    ItemDescription = db.TextProperty(required = False)
    dateAdded = db.DateTimeProperty(auto_now_add=True)
    ImageURL = db.LinkProperty(required = False)
    canTransfer = db.BooleanProperty(required = True)
    catagory = db.StringProperty()


class People(db.Model):
    email = db.StringProperty(required = True)
    name = db.StringProperty(required = True)
    phone = db.IntegerProperty(required = True)
    ImageURL = db.LinkProperty(required = False)
    items = db.StringListProperty()

class Catagory(db.Model):
    CatagoryName = db.StringProperty(required = True)
    CatagoryID = db.IntegerProperty(required = True)
    CatagoryDescription = db.TextProperty(required = True)
    ImageURL = db.LinkProperty(required = False)








class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class MainPage(Handler):
    def render_mainpage(self):
        Items3 = db.GqlQuery("SELECT * FROM Items3")
        names = db.GqlQuery("SELECT * FROM People")
        catagory = db.GqlQuery("SELECT * FROM Catagory")
        self.render("main.html", Items3 = Items3, names = names)

    def get(self):
        time.sleep(1)
        username = self.request.cookies.get("username", "error")
        if self.confirm_cookies():
            self.render_mainpage()
        else:
            self.redirect("/login")

    def confirm_cookies(self):
        #make sure cookie is found
        email = self.request.cookies.get("email", "error")
        print(email)
        return True




class NewItem(Handler):
    def render_newpost(self , ItemName ="", ItemDescription = "", ItemLocation = "41.896716, -87.643280", error = ""):
        self.render("newform.html", ItemName= ItemName, ItemDescription = ItemDescription, ItemLocation = ItemLocation, error = error)

    def get(self):
        self.render_newpost()

    def post(self):
        ItemName = self.request.get("ItemName")
        ItemDescription = self.request.get("ItemDescription")
        ItemLocation = self.request.get("ItemLocation")
        canTransfer = "True" == self.request.get("canTransfer")
        newitem = Items3(ItemName = ItemName, ItemID = 2343234, UserID = 33244334, ItemLocation = ItemLocation, isNeed = True, isCompleted = False, ItemDescription =ItemDescription, canTransfer = canTransfer)
            

        newitem.put()
        x = str(newitem.key().id())
        self.redirect("/")
        # else:
        #     error = "incomplete"
        #     self.render_newpost(ItemName, ItemDescription, Location, error)


class LoginItem(Handler):
    def render_newpost(self , ItemName ="", ItemDescription = "", ItemLocation = "41.896716, -87.643280", error = ""):
        self.render("newform.html", ItemName= ItemName, ItemDescription = ItemDescription, ItemLocation = ItemLocation, error = error)

    def get(self):
        self.render_newpost()


class SignUp(Handler):
    def get(self,username="",name_error="",phone="",phone_error=""):
        self.render("signup.html", username = username, name_error = name_error, phone = phone, phone_error = phone_error)

    def post(self, username="",name_error="",phone="",phone_error=""): 
        name_error = self.confirm_verify_username(self.request.get('username')) #################
        phone_error = self.confirm_email(self.request.get('phone')) #####################
        if  name_error =="" and phone_error=="":
            self.success(self.request.get('username'), self.request.get('phone'))
        else:
            self.render("signup.html", username = username, name_error = name_error, email = email, email_error = email_error)


    def success(self, username, email):
        #TO DO: hash cookie and login
        # hashedlogin = self.make_hash(username, password, email)
        # hashedlogin_db = hashedlogin.split(",")
        # username = unicodedata.normalize('NFKD', hashedlogin_db[0]).encode('ascii','ignore')
        # password = unicodedata.normalize('NFKD', hashedlogin_db[1]).encode('ascii','ignore')
        # salt = unicodedata.normalize('NFKD', hashedlogin_db[3]).encode('ascii','ignore')
        self.response.headers.append('set-cookie', unicodedata.normalize('NFKD', email).encode('ascii','ignore'))
        newuser = People(name = username, email = email)
        newuser.put()
        self.redirect("/")

    # def setcookie(name,email):
    #     expressions = {1:"password="}
    #     cookie = "login=" + hashedlogin
    #     cookie = unicodedata.normalize('NFKD', cookie).encode('ascii','ignore')
    #     self.response.headers.append('set-cookie', email)



    def confirm_verify_username(self, name):
        name_error = ""
        users = db.GqlQuery("SELECT * FROM Logins")
        for user in users:
            if name == user.username:
                name_error = "This username is aleady taken!"
        return name_error

    def confirm_phone(self, email):

        #proper phone 

        email_error = ""
        if not self.check_value(email,'email'):
            email_error="This email is not valid!"
        return ""
        #return email_error


app = webapp2.WSGIApplication([('/', MainPage),('/new/?', NewItem),('/login/?', LoginItem),('/signup/?', SignUp)], debug=True)

