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
import hashlib
import urllib2
import string
import packages
import geopy
#import appengine_utilities
#import pycrypto
from gaesessions import SessionMiddleware
from gaesessions import get_current_session



# from geopy import geocoders
from google.appengine.ext import db

print("here")
print(os.urandom(64).encode('hex'))

template_dir = os.path.join(os.path.dirname(__file__), 'templates/')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

class Inventory(db.Model):
    ItemName = db.StringProperty(required = True)
    phone = db.IntegerProperty(required = True)
    isNeed = db.BooleanProperty(required = True)
    isCompleted = db.BooleanProperty(required = True)
    ItemDescription = db.TextProperty(required = False)
    dateAdded = db.DateTimeProperty(auto_now_add=True)
    ImageURL = db.LinkProperty(required = False)
    canTransfer = db.BooleanProperty(required = True)
    catagory = db.StringProperty()
    location = db.GeoPtProperty()

class People(db.Model):
    name = db.StringProperty(required = True)
    phone = db.IntegerProperty(required = True)
    userhash = db.StringProperty(required = True)
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

    def sendmessage(self,phone,string):
        string = urllib.quote_plus(string)
        sendurl="https://api.tropo.com/1.0/sessions?action=create&token=23f4f85266b1644dba28170e130e1af478e4792e6e198c0292abd66d05fbc0cf5126442f4785049c150d04ae&myNumbers=" 
        sendurl= sendurl + "1" + str(phone)
        sendurl = sendurl + "&myText=" 
        sendurl = sendurl + string
        sendurl = sendurl + "&myURL=http://hackchicagoihaveineed.appspot.com/"
        print(phone + ": " + string)
        #urllib2.urlopen(sendurl).read()

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

    def setcookie(self, encryption):
        cookie = "encryption=" + encryption
        cookie = unicodedata.normalize('NFKD', cookie).encode('ascii','ignore')
        self.response.headers.add_header('set-cookie', cookie)

    def validateUser(self):
        curentlogin = self.request.cookies.get("phone", "error")
        if curentlogin == "error":
            self.redirect("/login")
        if not self.confirm_phone(self.request.cookies.get("phone", "error")) == "":
            self.redirect("/login")
        #implement bad cookie

    def check_password(self, one,two):
        return one==two

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

    def confirm_cookies(self):
        #make sure cookie is found
        phone = self.getUser()
        print(phone)
        return True

    def make_hash(self, username, phone, password):
        salt = hashlib.sha256(username).hexdigest()
        hash = hashlib.sha256(username + str(phone) + password + salt).hexdigest()
        return str(hash)
    
    def cleanPhone(self, phone):
        return int(re.sub("\D", "", phone))

    def decryprt(self, hash):
        return self


    def confirm_password(self, password, verify):
        password_error = ""
        if not self.check_value(password,'password'):
            password_error = "This password is not valid!"
        else:
            if self.check_password(password ,verify):
                password_error=""
            else:
                password_error = "These passwords are not the same!"
        return password_error


    # def encode(key, string):
    # encoded_chars = []
    # for i in xrange(string):
    #     key_c = key[i % len(key)]
    #     encoded_c = chr(ord(string[i]) + ord(encoded_c) % 256)
    #     encoded_chars.append(encoded_c)
    # encoded_string = "".join(encoded_chars)
    # return base64.urlsafe_b64encode(encoded_string)
    def getUser(self):
        return int(self.request.cookies.get("phone", "error"))
        
class MainPage(Handler):
    def render_mainpage(self):

        Inventory = db.GqlQuery("SELECT * FROM Inventory")
        names = db.GqlQuery("SELECT * FROM People")
        catagory = db.GqlQuery("SELECT * FROM Catagory")
        self.render("main.html", items = Inventory, names = names)

    def get(self):
        self.render_mainpage()

class NewItem(Handler):
    def render_newpost(self , ItemName ="", ItemDescription = "", ItemLocation = "", error = ""):
        #get location
        self.render("newform.html", ItemName= ItemName, ItemDescription = ItemDescription, ItemLocation = ItemLocation, error = error)

    def get(self):
        self.validateUser()
        self.render_newpost()

    def post(self):
        self.validateUser()
        ItemName = self.request.get("ItemName")
        ItemDescription = self.request.get("ItemDescription")
        ItemLocation = self.request.get("ItemLocation")
        canTransfer = self.request.get("canTransfer") == "True"
        isNeed = self.request.get("isNeed") == "True"
        catagory = self.request.get("catagory")
        phone = self.getUser() #needs proper encryption
        matches = self.findMatches(isNeed) #needs to be more efficient
        matches = self.findClosets(matches) #needs to sort by location
        if len(matches) == 0:
            self.render("emptymatchresults.html") #needs to contain data
        else: 
            self.render("pageofresults.html") #needs to contain data

    def findMatches(self, isNeed):
        needs = db.GqlQuery("SELECT * FROM Inventory")
        matchNeeds = {}
        matchHaves = {}
        for need in needs:
            if need.catagory == catagory:
                if not need.isCompleted:    
                    newitem = Inventory(ItemName = need.ItemName, catagory = need.catagory, phone = need.phone, location = need.location, isNeed = need.isNeed, isCompleted = need.isCompleted, ItemDescription = need.ItemDescription, canTransfer = need.canTransfer)
                    if need.isNeed:
                        matchNeeds[need.ItemName] = newitem
                    else:
                        matchHaves[need.ItemName] = newitem
        if isNeed:
            return matchNeeds
        else:
            return matchHaves

    def findClosets(self,matches):
        #matches = matches.sort()
        return matches

class LoginItem(Handler):
    def get(self, phone_error=""):
        session = get_current_session()
        self.render("login.html",phone_error = phone_error)

    def post(self, phone_error=""):
        phone = self.request.get('phone')
        phone_error = self.confirm_phone(self.request.get('phone'))
        phone = re.sub("\D", "", phone)
        if phone_error == "":
            phone_error = self.confirm_verify_phone(phone)
            if phone_error == "":
                session['phone'] = phone
                self.redirect("/")
        self.render("login.html", phone_error = phone_error)

class AddToDataBase(Handler):
    def get(self, phone_error=""):
        self.render("login.html",phone_error = phone_error)

    def post(self, phone_error=""):
        self.render("login.html", phone_error = phone_error)


class SignUp(Handler):
    def get(self,username="",name_error="", password = "", password_error = "", phone="",phone_error=""):
        session = get_current_session()

        self.render("signup.html", username = username, password = password, password_error = password_error, name_error = name_error, phone = phone, phone_error = phone_error)

    def post(self, username="",name_error="",phone="",password = "", password_error = "", phone_error=""): 
        phone = self.request.get('phone')
        phone_error = self.confirm_phone(self.request.get(phone))
        password_error = self.confirm_password(self.request.get('password'), self.request.get('verify'))
        phone = self.cleanPhone(phone)
        phone_error = self.confirm_phone(self.request.get('phone')) #####################
        if phone_error == "":
            name_error = self.confirm_verify_username(self.request.get('username'),phone) #################
        if  name_error =="" and phone_error=="" and password_error == "":
            self.success(self.request.get('username'), phone, password,session)
        else:
            self.render("signup.html", username = username, name_error = name_error, phone = phone, phone_error = phone_error)

    def success(self, username, phone,password,session):
        userhash = self.make_hash(username, phone,password)
        session['user'] = userhash
        session['phone'] = phone
        newuser = People(name = username, password = password, userhash= userhash, phone = self.cleanPhone(phone))
        newuser.put()
        self.redirect("/")


app = webapp2.WSGIApplication([('/', MainPage),('/new/?', NewItem),('/login/?', LoginItem),('/add/?', AddToDataBase),('/signup/?', SignUp)], debug=True)

