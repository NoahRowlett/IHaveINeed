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
import string
#import appengine_utilities
#import pycrypto
from webapp2_extras import sessions

config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'c4047563e84e0dab8ddfbf78780542e59713396005fa232ec017e5a852eb7d687f28ff4b341f2802a4d597bd1357bdf14d4ba5c344c555b44cf55ed4f36d547c',
}

universalsalt = "dog"

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
        expressions = {"password":"^.{3,20}$","username":"^[a-zA-Z0-9_-]{3,20}$", "phone":"^\D?(\d{3})\D?\D?(\d{3})\D?(\d{4})$" }
        try:
            (re.findall(expressions[kind], value)[0] == value)
        except :
            return False
        return True

    def isPhoneinDatabase(self, phone):
        name_error = "number already in database"
        result = db.GqlQuery("SELECT * FROM People WHERE phone = %s" % phone)

        # users = db.GqlQuery("SELECT * FROM People")
        # for user in users:
        #     if str(db.PhoneNumber(phone)) == str(user.phone):
        #         name_error = "number already in database"
        print("here")
        print(result)
        print(result.count(1))
        if not result.count(1):
            name_error = ""
        print(name_error)
        return name_error

    def setcookie(self, encryption):
        cookie = "encryption=" + encryption
        cookie = unicodedata.normalize('NFKD', cookie).encode('ascii','ignore')
        self.response.headers.add_header('set-cookie', cookie)

    def validateUser(self):
        print('validation not setup')
        # phone = self.session.get('phone')
        # hashed = self.session.get('hash')
        # phone = self.cleanPhone(phone)
        # print(phone)
        # user = db.GqlQuery("SELECT * FROM People WHERE phone = %s" % phone)[0] #gets what should be only user with number
        # if not user.userhash == hashed:
        #     self.redirect('/')

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
        all=string.maketrans('','')
        nodigs=all.translate(all, string.digits)
        return int(str(phone).translate(all, nodigs))

    def decryprt(self, hash):
        return self

    def databaseIsEmpty(self, database):
        empty = database.all()
        return empty.count(1)


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

    def getUser(self):
        return int(self.request.cookies.get("phone", "error"))
 

class BaseHandler(webapp2.RequestHandler):
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()


class MainPage(BaseHandler, Handler):
    def render_mainpage(self):
        Inventory = db.GqlQuery("SELECT * FROM Inventory")
        names = db.GqlQuery("SELECT * FROM People")
        catagory = db.GqlQuery("SELECT * FROM Catagory")
        self.render("main.html", items = Inventory, names = names)

    def get(self):
        username = self.session.get('username')
        phone = self.session.get('phone')
        if username and phone:
            self.response.write('welcome ' + username)
        elif phone or username:
            self.redirect('/logout')
        else:
            self.response.write('You should sign up or sign in.')
        self.render_mainpage()

class Logout(BaseHandler, Handler):
    def get(self):
        self.session.clear()
        self.redirect('/')

class NewItem(BaseHandler, Handler):
    def render_newpost(self , ItemName ="", ItemDescription = "", ItemLocation = "", error = ""):
        self.render("newform.html", ItemName= ItemName, ItemDescription = ItemDescription, ItemLocation = ItemLocation, error = error)

    def get(self):
        self.validateUser()
        self.render_newpost()

    def post(self):
        ItemName = self.request.get("ItemName")
        ItemDescription = self.request.get("ItemDescription")
        ItemLocation = self.request.get("ItemLocation")
        canTransfer = self.request.get("canTransfer") == "True"
        isNeed = self.request.get("isNeed") == "True"
        catagory = self.request.get("catagory")

        phone = self.session.get('phone')
        phone = self.cleanPhone(phone)
        newitem = Inventory(ItemName = ItemName, catagory = catagory, phone = phone, location = ItemLocation, isNeed = isNeed, isCompleted = False, ItemDescription = ItemDescription, canTransfer = canTransfer)






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

class LoginItem(BaseHandler, Handler):
    def get(self, phone_error=""):
        self.render("login.html",phone_error = "")

    def post(self, phone_error=""):
        phone_error=""
        phone = self.request.get('phone')
        phone_error = self.confirm_phone(self.request.get('phone')) #confirms the number is valid type
        phone = re.sub("\D", "", phone) #cleans numbers?
        # user = People.all()
        # if user.count(1):
        #     phone_error = "empty"
        if phone_error == "":
            phone_error = self.isPhoneinDatabase(phone) #ensures phone is in database
            if not phone_error == "":
                phone = self.cleanPhone(phone) #cleans numbers
                user = db.GqlQuery("SELECT * FROM People WHERE phone = %s" % phone)[0] #gets what should be only user with number
                print(user.name, phone, self.request.get('password'))
                testhash = self.make_hash(user.name, phone, self.request.get('password')) #generates hash with input number, password name drawn from database
                print(testhash)
                print(user.userhash) #hash on database
                print(user.name)
                if testhash == user.userhash: #compares local hash with hash in database
                    phone_error = ""
                    self.session['username'] = user.name 
                    self.session['phone'] = phone
                    self.session['hash'] = testhash
                else:
                    phone_error = "Password and number do not match"
            # else:
                # phone_error = "Number not in Database"
        # else:
            # phone_error = "Invalid Number"
        print(phone_error)
        if not phone_error:
            self.redirect("/")
        else:
            self.render("login.html", phone_error = phone_error)

class AddToDataBase(BaseHandler, Handler):
    def get(self, phone_error=""):
        self.render("login.html",phone_error = phone_error)

    def post(self, phone_error=""):
        self.render("login.html", phone_error = phone_error)


class SignUp(BaseHandler, Handler):
    def get(self,username="",name_error="", password = "", password_error = "", phone="",phone_error=""):
        self.render("signup.html", username = username, password = password, password_error = password_error, name_error = name_error, phone = phone, phone_error = phone_error)

    def post(self, username="",name_error="",phone="",password = "", password_error = "", phone_error=""): 
        phone = self.cleanPhone(self.request.get('phone')) #stores phone
        phone_error = self.confirm_phone(self.request.get('phone')) #checks if number is valid
        password_error = self.confirm_password(self.request.get('password'), self.request.get('verify'))#checks if passwords match
        phone_error = self.isPhoneinDatabase(phone)
        if  name_error =="" and phone_error=="" and password_error == "":
            self.success(self.request.get('username'), phone, self.request.get('password'))
        else:
            self.render("signup.html", username = self.request.get('username'), name_error = name_error, phone = self.request.get('phone'), phone_error = phone_error)

    def success(self, username, phone,password):
        phone = self.cleanPhone(phone)
        print(username, phone, password)
        userhash = self.make_hash(username, phone, password)
        self.session['username'] = username
        self.session['phone'] = phone
        self.session['hash'] = userhash
        newuser = People(name = username, password = password, userhash= userhash, phone = phone)
        newuser.put()
        self.redirect("/")


app = webapp2.WSGIApplication([('/', MainPage),
    ('/new/?', NewItem),
    ('/login/?', LoginItem),
    ('/add/?', AddToDataBase),
    ('/signup/?', SignUp),
    ('/logout', Logout)],
     config=config, debug=True)

def main():
    app.run()

if __name__ == '__main__':
    main()
