#!/usr/bin/env python

# Copyright 2016 Google Inc.
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

# [START imports]
import os
import urllib
import random

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
# [END imports]

DEFAULT_GUESTBOOK_NAME = 'default_guestbook'
DEFAULT_RESOURCE_NAME = 'default_resource'

# We set a parent key on the 'Greetings' to ensure that they are all
# in the same entity group. Queries across the single entity group
# will be consistent. However, the write rate should be limited to
# ~1/second.

def guestbook_key(guestbook_name=DEFAULT_GUESTBOOK_NAME):
    """Constructs a Datastore key for a Guestbook entity.

    We use guestbook_name as the key.
    """
    return ndb.Key('Guestbook', guestbook_name)

# [START greeting]
class Author(ndb.Model):
    """Sub model for representing an author."""
    identity = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(indexed=False)


class Greeting(ndb.Model):
    """A main model for representing an individual Guestbook entry."""
    author = ndb.StructuredProperty(Author)
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)
# [END greeting]
class Resource(ndb.Model):
    resource_Name=ndb.StringProperty(indexed=True)
    resource_Owner=ndb.StringProperty(indexed=True)
    resource_StartTime=ndb.StringProperty(indexed=True)
    resource_EndTime=ndb.StringProperty(indexed=True)
    resource_tag=ndb.StringProperty(indexed=True)
    date = ndb.DateTimeProperty(auto_now_add=True)
    primaryKey=ndb.StringProperty(indexed=True)

# [START main_page]
class MainPage(webapp2.RequestHandler):

    def get(self):
        guestbook_name = self.request.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
        greetings_query = Greeting.query(
            ancestor=guestbook_key(guestbook_name)).order(-Greeting.date)
        greetings = greetings_query.fetch(10)
        
        resource_query = Resource.query().order(-Resource.date)
        resources = resource_query.fetch()
        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
        print resources
        #print greetings
        template_values = {
            'user': user,
            'greetings': greetings,
            'resources': resources,
            'guestbook_name': urllib.quote_plus(guestbook_name),
            'url': url,
            'url_linktext': url_linktext,
            'username' : user.nickname().split("@")[0]
        }
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))
# [END main_page]


# [START guestbook]
class Guestbook(webapp2.RequestHandler):

    def post(self):
        # We set the same parent key on the 'Greeting' to ensure each
        # Greeting is in the same entity group. Queries across the
        # single entity group will be consistent. However, the write
        # rate to a single entity group should be limited to
        # ~1/second.
        guestbook_name = self.request.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
        greeting = Greeting(parent=guestbook_key(guestbook_name))

        if users.get_current_user():
            greeting.author = Author(
                    identity=users.get_current_user().user_id(),
                    email=users.get_current_user().email())

        greeting.content = self.request.get('content')
        greeting.put()

        query_params = {'guestbook_name': guestbook_name}
        self.redirect('/?' + urllib.urlencode(query_params))
# [END guestbook]

    
class AddResource(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        if user:
            resource = Resource()            
            resource.resource_Name = self.request.get('resourceName')
            resource.resource_StartTime = self.request.get('startTime')
            resource.resource_EndTime = self.request.get('endTime')
            print str(self.request.get('endTime'))
            print self.request.get('startTime')
            resource.resource_tag = self.request.get('tags')
            resource.primaryKey=str(random.randint(100000,1000000))
            resource.resource_Owner=str(user.email())
            resource.put()
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
        template_values = {
            'isSuccess': '1',
            'user': user,
            'username' : user.nickname().split("@")[0],
            'url': url,
            'url_linktext': url_linktext,
            }
        
        template = JINJA_ENVIRONMENT.get_template('newResource.html')
        self.response.write(template.render(template_values))
        
    def get(self):
        user = users.get_current_user()
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
        template_values = {
            'user': user,
            'username' : user.nickname().split("@")[0],
            'url': url,
            'url_linktext': url_linktext,
            }
        template = JINJA_ENVIRONMENT.get_template('newResource.html')
        self.response.write(template.render(template_values))
        
class AddReservation(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        if user:
            resource = Resource()            
            resource.resource_Name = self.request.get('resourceName')
            resource.resource_StartTime = self.request.get('startTime')
            resource.resource_EndTime = self.request.get('endTime')
            print str(self.request.get('endTime'))
            print self.request.get('startTime')
            resource.resource_tag = self.request.get('tags')
            resource.primaryKey=str(random.randint(100000,1000000))
            resource.resource_Owner=str(user.email())
            resource.put()
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
        template_values = {
            'isSuccess': '1',
            'user': user,
            'username' : user.nickname().split("@")[0],
            'url': url,
            'url_linktext': url_linktext,
            }
        
        template = JINJA_ENVIRONMENT.get_template('newReservations.html')
        self.response.write(template.render(template_values))
        
    def get(self):
        user = users.get_current_user()
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
        template_values = {
            'user': user,
            'username' : user.nickname().split("@")[0],
            'url': url,
            'url_linktext': url_linktext,
            }
        template = JINJA_ENVIRONMENT.get_template('newReservation.html')
        self.response.write(template.render(template_values))

class ViewResource(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        if user:
            resource = Resource()            
            resource.resource_Name = self.request.get('resourceName')
            resource.resource_StartTime = self.request.get('startTime')
            resource.resource_EndTime = self.request.get('endTime')
            resource.resource_tag = self.request.get('tags')
            resource.resource_Owner=str(user.email())
            resource.put()
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
        template_values = {
            'isSuccess': '1',
            'user': user,
            'username' : user.nickname().split("@")[0],
            'url': url,
            'url_linktext': url_linktext,
            }
        
        template = JINJA_ENVIRONMENT.get_template('newResource.html')
        self.response.write(template.render(template_values))
        
    def get(self):
        user = users.get_current_user()
        isEditable=True
        keyVal=self.request.get('keyVal')
        print keyVal
        outputResource=Resource.query(Resource.primaryKey==keyVal).fetch()
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
        print outputResource
        template_values = {
            'isEditable': isEditable,
            'outputResource': outputResource,
            'user': user,
            'username' : user.nickname().split("@")[0],
            'url': url,
            'url_linktext': url_linktext,
        }
        template = JINJA_ENVIRONMENT.get_template('viewResource.html')
        self.response.write(template.render(template_values))

# [START app]
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/sign', Guestbook),
    ('/addResource',AddResource),
    ('/addReservation',AddReservation),
    ('/viewResource',ViewResource)
], debug=True)
# [END app]
