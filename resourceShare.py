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
import random
import datetime

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
def filterResourcesByOwner(resourceList):
    returnList=[]
    for resource in resourceList:
        if resource.resource_Owner == users.get_current_user().email():
            returnList.append(resource)
    return returnList        

def filterReservationsOnEndTime(reservationList):
    returnList=[]
    for reservation in reservationList:
        presentDateTime= datetime.datetime.now()- datetime.timedelta(minutes=240)
        converteddate=datetime.datetime.combine(presentDateTime.date(),datetime.datetime.strptime(reservation.reservation_EndTime,'%H:%M').time())
        #print datetime.datetime.now().date()
        #print datetime.datetime.strptime(reservation.reservation_EndTime,'%H:%M').time()
        #print (converteddate-presentDateTime).total_seconds()
        if (converteddate-presentDateTime).total_seconds()>0:
            #print "Yess"
            returnList.append(reservation)
        #print returnList
    return returnList        

def filterReservationsByOwner(reservationList):
    returnList=[]
    for reservation in reservationList:
        if reservation.reservation_Owner == users.get_current_user().email():
            returnList.append(reservation)
    return returnList    
# [START greeting]


# [END greeting]
class Resource(ndb.Model):
    resource_Name=ndb.StringProperty(indexed=True)
    resource_Owner=ndb.StringProperty(indexed=True)
    resource_StartTime=ndb.StringProperty(indexed=False)
    resource_EndTime=ndb.StringProperty(indexed=False)
    resource_tag=ndb.StringProperty(repeated=True)
    date = ndb.DateTimeProperty(auto_now_add=True)
    primaryKey=ndb.StringProperty(indexed=True)
    resource_Duration=ndb.IntegerProperty(indexed=True)
    totalReservations=ndb.IntegerProperty(indexed=False)
    justCreated=ndb.IntegerProperty(indexed=False)
    
class Reservation(ndb.Model):
    resource_Name=ndb.StringProperty(indexed=True)
    resource_PrimaryKey=ndb.StringProperty(indexed=True)
    reservation_Owner=ndb.StringProperty(indexed=True)
    reservation_StartTime=ndb.StringProperty(indexed=True)
    reservation_EndTime=ndb.StringProperty(indexed=True)
    reservation_Notes=ndb.StringProperty(indexed=True)
    date = ndb.DateTimeProperty(auto_now_add=False)
    primaryKey=ndb.StringProperty(indexed=True)
    reservation_Duration=ndb.IntegerProperty(indexed=True)

# [START main_page]
class MainPage(webapp2.RequestHandler):

    def get(self):
        resource_query = Resource.query().order(-Resource.date)
        resources = resource_query.fetch()
        reservationList=Reservation.query().order(Reservation.reservation_StartTime).fetch()
        user = users.get_current_user()
        showFull=True
        keyVal=self.request.get('keyVal')
        if(len(keyVal)>1):
            showFull=False
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
        #print resources
        filteredResources=filterResourcesByOwner(resources)
        #print filteredResources
        filteredReservations=filterReservationsOnEndTime(filterReservationsByOwner(reservationList))
        #print filteredReservations
        template_values = {
            'user': user,
            'resources': resources,
            'userResources': filteredResources,
            'userReservations': filteredReservations,
            'url': url,
            'url_linktext': url_linktext,
            'username' : user.nickname().split("@")[0],
            'showFull':showFull,
        }
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))
# [END main_page]

    
class AddResource(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        if user:
            resource = Resource()            
            resource.resource_Name = self.request.get('resourceName')
            resource.resource_StartTime = self.request.get('startTime')
            resource.resource_EndTime = self.request.get('endTime')
            differenceTime= datetime.datetime.strptime(self.request.get('endTime'),'%H:%M')-datetime.datetime.strptime(self.request.get('startTime'),'%H:%M')
            resource.resource_Duration= int((differenceTime.total_seconds())/60)
            #print self.request.get('startTime')
            tagList=self.request.get('tags').replace(';',',').split(',')
            filteredTagList=[]
            for tag in tagList:
                t=tag.strip()
                if len(t)>0:
                    filteredTagList.append(t)
                    #print "test "+t
                
                
            resource.resource_tag = filteredTagList
            resource.primaryKey=str(random.randint(100000,1000000))
            resource.resource_Owner=str(user.email())
            resource.totalReservations=0
            resource.justCreated=1
            presentDateTime1= datetime.datetime.now()- datetime.timedelta(minutes=240)
            presentDateTime= datetime.datetime.combine(presentDateTime1.date(),datetime.datetime.strptime("00:00",'%H:%M').time())
            resource.date=presentDateTime
            resource.put()
            self.redirect('/')
        
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
            reservation = Reservation()
            reservation.resource_Name = self.request.get('resourceName')
            reservation.resource_PrimaryKey = self.request.get('resourceKey')
            #print self.request.get('resourcePrimaryKey')
            reservingResourceDetails=Resource.query(Resource.primaryKey==str(self.request.get('resourcePrimaryKey'))).fetch()
            reservation.reservation_StartTime = self.request.get('startTime')
            #reservation.reservation_EndTime = self.request.get('endTime')
            #print str(self.request.get('endTime'))
            #print self.request.get('startTime')
            #print reservingResourceDetails;
            reservation.reservation_Notes = self.request.get('notes')
            reservation.primaryKey=str(random.randint(100000,1000000))
            reservation.reservation_Owner=str(user.email())
            reservation.reservation_Duration= int(self.request.get('duration'))
            endTime= str((datetime.datetime.strptime(self.request.get('startTime'),'%H:%M')+datetime.timedelta(minutes=(int(self.request.get('duration'))))))
            times=endTime.split(":")
            print times[0].split(" ")[1]+":"+times[1]
            reservation.reservation_EndTime=times[0].split(" ")[1]+":"+times[1]
            rquery=Resource.query(Resource.primaryKey==str(self.request.get('resourcePrimaryKey'))).fetch()
            presentDateTime= datetime.datetime.now()- datetime.timedelta(minutes=240)

            rquery[0].date=presentDateTime
            rquery[0].totalReservations+=1
            rquery[0].justCreated=0
            rquery[0].put()
            reservation.put()
        self.redirect('/')
        
    def get(self):
        
        user = users.get_current_user()
        url = users.create_logout_url(self.request.uri)
        keyVal=self.request.get('keyVal')
        reservingResource=Resource.query(Resource.primaryKey==keyVal).fetch()
        url_linktext = 'Logout'
        template_values = {
            'user': user,
            'username' : user.nickname().split("@")[0],
            'reservingResource':reservingResource[0].resource_Name,
            'reservingResourceDetails':reservingResource,
            'reservingResourceKey': reservingResource[0].primaryKey,
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
        isEditable=False
        keyVal=self.request.get('keyVal')
        #print keyVal
        #print user.email()
        outputResource=Resource.query(Resource.primaryKey==keyVal).fetch()
        #print outputResource[0].resource_Owner
        upcomingReservations=[]
        allReservations=Reservation.query().order(Reservation.reservation_StartTime).fetch()
        #print filterReservationsOnEndTime(filterReservationsByOwner(allReservations))
        for reservation in filterReservationsOnEndTime(filterReservationsByOwner(allReservations)):
            if reservation.resource_PrimaryKey==keyVal:
                upcomingReservations.append(reservation)
        #print upcomingReservations
        if str(outputResource[0].resource_Owner) == str(user.email()):
            isEditable=True
        #print isEditable
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
        #print outputResource
        template_values = {
            'isEditable': isEditable,
            'outputResource': outputResource,
            'upcomingReservations':upcomingReservations,
            'user': user,
            'username' : user.nickname().split("@")[0],
            'url': url,
            'url_linktext': url_linktext,
        }
        template = JINJA_ENVIRONMENT.get_template('viewResource.html')
        self.response.write(template.render(template_values))

class ViewReservation(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        if user:
            resource = Resource()            
            resource.resource_Name = self.request.get('resourceName')
            resource.resource_StartTime = self.request.get('startTime')
            resource.resource_EndTime = self.request.get('endTime')
            resource.resource_tag = self.request.get('notes')
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
        isEditable=False
        keyVal=self.request.get('keyVal')
        #print keyVal
        #print user.email()
        outputReservation=Reservation.query(Reservation.primaryKey==keyVal).fetch()
        #print outputResource[0].resource_Owner
        if str(outputReservation[0].reservation_Owner) == str(user.email()):
            isEditable=True
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
        #print outputReservation
        template_values = {
            'isEditable': isEditable,
            'outputReservation': outputReservation,
            'user': user,
            'username' : user.nickname().split("@")[0],
            'url': url,
            'url_linktext': url_linktext,
        }
        template = JINJA_ENVIRONMENT.get_template('viewReservation.html')
        self.response.write(template.render(template_values))
        
class EditResource(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        if user:
            rquery=Resource.query(Resource.primaryKey==str(self.request.get('resourceKey'))).fetch()
            rquery[0].resource_Name = self.request.get('resourceName')
            rquery[0].resource_StartTime = self.request.get('startTime')
            rquery[0].resource_EndTime = self.request.get('endTime')
            differenceTime= datetime.datetime.strptime(self.request.get('endTime'),'%H:%M')-datetime.datetime.strptime(self.request.get('startTime'),'%H:%M')
            rquery[0].resource_Duration= int((differenceTime.total_seconds())/60)
            #print self.request.get('startTime')
            rquery[0].resource_tag = self.request.get('tags')
            resourceKey=rquery[0].primaryKey
            reservationQuery=Reservation.query(Reservation.resource_PrimaryKey==str(resourceKey)).fetch()
            for res in reservationQuery:
                res.resource_Name=self.request.get('resourceName')
                res.put()
            rquery[0].put()
            
        self.redirect('/')

class DeleteReservation(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        if user:
            rquery=Reservation.query(Reservation.primaryKey==str(self.request.get('reservationKey'))).fetch()
            rquery[0].resource_tag = self.request.get('tags')
            res=Resource.query(Resource.primaryKey==rquery[0].resource_PrimaryKey).fetch()
            res[0].totalReservations-=1;
            res[0].put()
            rquery[0].key.delete()
            
        self.redirect('/')
        
class Tags(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        tagName=self.request.get('tag')
        allResources=Resource.query().fetch()
        tagresources=[];
        for resource in allResources:
            if tagName in resource.resource_tag:
                tagresources.append(resource)
                
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
        template_values = {
            'user': user,
            'username' : user.nickname().split("@")[0],
            'url': url,
            'url_linktext': url_linktext,
            'tagName':tagName,
            'tagResources': tagresources,
        }
        template = JINJA_ENVIRONMENT.get_template('tag.html')
        self.response.write(template.render(template_values))        
             
# [START app]
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/viewReservation',ViewReservation),
    ('/addResource',AddResource),
    ('/addReservation',AddReservation),
    ('/viewResource',ViewResource),
    ('/deleteReservation',DeleteReservation),
    ('/tags',Tags),
    ('/editResource',EditResource)
], debug=True)
# [END app]

