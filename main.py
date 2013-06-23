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
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates/')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)


class Items2(db.Model):
    ItemName = db.StringProperty(required = True)
    ItemID = db.IntegerProperty(required = True)
    UserID = db.IntegerProperty(required = True)
    ItemLocation = db.GeoPtProperty(required = True)
    isNeed = db.BooleanProperty(required = True)
    isCompleted = db.BooleanProperty(required = True)
    ItemDescription = db.TextProperty(required = False)
    dateAdded = db.DateTimeProperty(auto_now_add=True)
    ImageURL = db.LinkProperty(required = False)
    canTransfer = db.BooleanProperty(required = True)


class People(db.Model):
    UserID = db.IntegerProperty(required = True)
    firstname = db.StringProperty(required = True)
    lastname = db.StringProperty(required = True)
    Address = db.PostalAddressProperty(required = True)
    PhoneNumber = db.PhoneNumberProperty(required = True)
    ImageURL = db.LinkProperty(required = False)

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
        items2 = db.GqlQuery("SELECT * FROM Items2")
        names = db.GqlQuery("SELECT * FROM People")
        catagory = db.GqlQuery("SELECT * FROM Catagory")
        self.render("main.html", items = items2, names = names)

    def get(self):
        self.render_mainpage()

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
        newitem = Items2(ItemName = ItemName, ItemID = 2343234, UserID = 33244334, ItemLocation = ItemLocation, isNeed = True, isCompleted = False, ItemDescription =ItemDescription, canTransfer = canTransfer)
            

        newitem.put()
        x = str(newitem.key().id())
        self.redirect("/")
        # else:
        #     error = "incomplete"
        #     self.render_newpost(ItemName, ItemDescription, Location, error)





app = webapp2.WSGIApplication([('/', MainPage),('/new/?', NewItem)], debug=True)

