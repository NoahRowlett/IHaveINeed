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
import urllib
import re
import urllib2
import string
from geopy import geocoders
from google.appengine.ext import db



template_dir = os.path.join(os.path.dirname(__file__), 'templates/')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)


class Items4(db.Model):
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
    location = db.GeoPtProperty()

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


class HomePage(Handler):
    def render_mainpage(self):
        self.render("index.html")
    def get(self):
        self.render_mainpage()

class MainPage(Handler):
    def render_mainpage(self):

        Items4 = db.GqlQuery("SELECT * FROM Items4")
        names = db.GqlQuery("SELECT * FROM People")
        catagory = db.GqlQuery("SELECT * FROM Catagory")
        self.render("main.html", Items4 = Items4, names = names)

    def get(self):
        self.render_mainpage()

        # time.sleep(1)
        # username = self.request.cookies.get("username", "error")http://hackchicagoihaveineed.appspot.com/
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
    def render_newpost(self , ItemName ="", ItemDescription = "", ItemLocation = "", error = ""):
        #get location
        self.render("newform.html", ItemName= ItemName, ItemDescription = ItemDescription, ItemLocation = ItemLocation, error = error)

    def get(self):
        self.render_newpost()

    def post(self):
        ItemName = self.request.get("ItemName")
        ItemDescription = self.request.get("ItemDescription")
        ItemLocation = self.request.get("ItemLocation")
        # g = geocoders.GoogleV3()
        # place, (lat, lng) = g.geocode(ItemLocation)

        canTransfer = self.request.get("canTransfer")
        canTransfer = canTransfer == "True"
        isNeed = self.request.get("isNeed")
        isNeed = isNeed == "True"
  


        catagory = self.request.get("catagory")
        print(catagory)
        phone = int(self.request.cookies.get("phone", "error"))
        found = False
        if isNeed:
            print("here")
            needs = db.GqlQuery("SELECT * FROM Items4")
            for need in needs:
                print(need.catagory)
                if need.isNeed:
                    if need.catagory == catagory:
                        string = "Someone needs what you have. His name is %s. His number is %s"
                        self.sendmessage(int(str(need.phone)), string)
                        string = "Someone has what you need. His name is %s. His number is %s"
                        self.sendmessage(phone, string)
                        found = True            
        else:
            print("there")
            needs = db.GqlQuery("SELECT * FROM Items4")
            for need in needs:
                if need.isNeed:
                    if need.catagory == catagory:
                        string = "Someone has what you need. His name is %s. His number is %s"
                        self.sendmessage(int(str(need.phone)), string)
                        string = "Someone needs what you have. His name is %s. His number is %s"
                        self.sendmessage(phone, string)
                        
                        found = True
        #sort by location
        if found:

            ##matches page
            print("THERE WERE MATCHES")
        print("nowhere")
        if not found:
            newitem = Items4(ItemName = ItemName, catagory = catagory, phone = phone, ItemLocation = ItemLocation, isNeed = isNeed, isCompleted = False, ItemDescription =ItemDescription, canTransfer = canTransfer)
            newitem.put()
        self.redirect("/home")

    def sendmessage(self,phone, string):
        string = urllib.quote_plus(string)
        sendurl="https://api.tropo.com/1.0/sessions?action=create&token=23f4f85266b1644dba28170e130e1af478e4792e6e198c0292abd66d05fbc0cf5126442f4785049c150d04ae&myNumbers=" 
        sendurl= sendurl + "1" + str(phone)
        sendurl = sendurl + "&myText=" 
        sendurl = sendurl + string
        sendurl = sendurl + "&myURL=http://hackchicagoihaveineed.appspot.com/"
        urllib2.urlopen(sendurl).read()


class LoginItem(Handler):
    def get(self, phone_error=""):
        self.render("login.html",phone_error = phone_error)

    def post(self, phone_error=""):
        phone = self.request.get('phone')
        phone_error = self.confirm_phone(self.request.get('phone'))
        phone = re.sub("\D", "", phone)
        if phone_error == "":
            phone_error = self.confirm_verify_phone(phone)
            if phone_error == "":
                self.setcookie(phone)
                self.redirect("/home")
        self.render("login.html", phone_error = phone_error)

    def confirm_phone(self, phone):
        phone_error = "That is not a valid number"
        if self.check_value(phone, "phone"):
            phone_error = ""
        return phone_error

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

    def confirm_verify_phone(self, phone):
        name_error = ""
        users = db.GqlQuery("SELECT * FROM People")
        for user in users:
            if str(db.PhoneNumber(phone)) == str(user.phone):
                name_error = ""
        return name_error
    def setcookie(self,phone):
        cookie = "phone=" + phone
        cookie = unicodedata.normalize('NFKD', cookie).encode('ascii','ignore')
        self.response.headers.add_header('set-cookie', cookie)






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
        self.setcookie(phone)
        newuser = People(name = username, phone = int(phone))
        newuser.put()
        self.redirect("/home")

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
        return phone_error
        


app = webapp2.WSGIApplication([('/', HomePage),('/home', MainPage),('/new/?', NewItem),('/login/?', LoginItem),('/signup/?', SignUp)], debug=True)

