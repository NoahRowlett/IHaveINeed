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
import unicodedata
import re
import string
from google.appengine.ext import db



template_dir = os.path.join(os.path.dirname(__file__), 'templates/')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)


class Items3(db.Model):
    ItemName = db.StringProperty(required = True)
    phone = db.IntegerProperty(required = True)
    isNeed = db.BooleanProperty(required = True)
    isCompleted = db.BooleanProperty(required = True)
    ItemDescription = db.TextProperty(required = False)
    dateAdded = db.DateTimeProperty(auto_now_add=True)
    ImageURL = db.LinkProperty(required = False)
    canTransfer = db.BooleanProperty(required = True)
    catagory = db.StringProperty()


class People(db.Model):
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
        self.render_mainpage()

        # time.sleep(1)
        # username = self.request.cookies.get("username", "error")
        # if self.confirm_cookies():
        #     self.render_mainpage()
        # else:
        #     self.redirect("/login")

    def confirm_cookies(self):
        #make sure cookie is found
        phone = self.request.cookies.get("phone", "error")
        print(phone)
        return True




class NewItem(Handler):
    def render_newpost(self , ItemName ="", ItemDescription = "", ItemLocation = "41.896716, -87.643280", error = ""):
        ##add have or need 

        self.render("newform.html", ItemName= ItemName, ItemDescription = ItemDescription, ItemLocation = ItemLocation, error = error)

    def get(self):
        self.render_newpost()

    def post(self):


        ItemName = self.request.get("ItemName")
        ItemDescription = self.request.get("ItemDescription")
        ItemLocation = self.request.get("ItemLocation")
        canTransfer = "True" == self.request.get("canTransfer")
        isNeed = "True" == self.request.get("isNeed")
        
        
        ##have or ned = "True" == self.request.get("have or ned")
        #result= False
        #if haveorneed:
            #run through code and see if there is a matcnh
        #else
        #if result:
        phone = int(self.request.cookies.get("phone", "error"))

        newitem = Items3(ItemName = ItemName, phone = phone, ItemID = 2343234, ItemLocation = ItemLocation, isNeed = True, isCompleted = False, ItemDescription =ItemDescription, canTransfer = canTransfer)
        newitem.put()
        x = str(newitem.key().id())
        #else:
        #use tropo api to notify other person





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
        phone = self.request.get('phone')
        phone_error = self.confirm_phone(self.request.get(phone))



        phone = re.sub("\D", "", phone)
        print(phone)
        phone_error = self.confirm_phone(self.request.get('phone')) #####################
        if phone_error == "":
            name_error = self.confirm_verify_username(self.request.get('username'),phone) #################
        if  name_error =="" and phone_error=="":
            self.success(self.request.get('username'), phone)
        else:
            self.render("signup.html", username = username, name_error = name_error, phone = phone, phone_error = phone_error)




    def success(self, username, phone):
        #TO DO: hash cookie and login
        # hashedlogin = self.make_hash(username, password, email)
        # hashedlogin_db = hashedlogin.split(",")
        # username = unicodedata.normalize('NFKD', hashedlogin_db[0]).encode('ascii','ignore')
        # password = unicodedata.normalize('NFKD', hashedlogin_db[1]).encode('ascii','ignore')
        # salt = unicodedata.normalize('NFKD', hashedlogin_db[3]).encode('ascii','ignore')
        self.setcookie(phone)

        newuser = People(name = username, phone = int(phone))
        newuser.put()
        self.redirect("/")

    def setcookie(self,phone):
        cookie = "phone=" + phone
        cookie = unicodedata.normalize('NFKD', cookie).encode('ascii','ignore')
        self.response.headers.add_header('set-cookie', cookie)

    def check_value(self, value,kind):
        expressions = {"email":"^[\S]+@[\S]+\.[\S]+$","password":"^.{3,20}$","username":"^[a-zA-Z0-9_-]{3,20}$", "phone":"^\D?(\d{3})\D?\D?(\d{3})\D?(\d{4})$" }
        if kind =="email": 
            if value =="":
                return True
        try:
            (re.findall(expressions[kind], value)[0] == value)
        except :
            return False
        return True



    def confirm_verify_username(self, name, phone):
        name_error = ""
        users = db.GqlQuery("SELECT * FROM People")
        for user in users:
            if name == user.name and str(db.PhoneNumber(phone)) == str(user.phone):
                
                name_error = "This account already exists!"
        return name_error

    def confirm_phone(self, phone):
        phone_error = "That is not a valid number"
        if self.check_value(phone, "phone"):
            phone_error = ""
        print(phone_error)
        return phone_error
        


app = webapp2.WSGIApplication([('/', MainPage),('/new/?', NewItem),('/login/?', LoginItem),('/signup/?', SignUp)], debug=True)

