# project/main/views.py


#################
#### imports ####
#################
from project import db, bcrypt

from flask import redirect
from flask.ext.login import login_user, logout_user, \
  login_required, current_user
from flask import render_template, Blueprint, request, json
from flask.ext.login import login_required
from project.models import User
from werkzeug.security import generate_password_hash, \
     check_password_hash

from werkzeug.security import generate_password_hash, check_password_hash

from flask_wtf import Form
from wtforms import validators
from wtforms import TextField, StringField, SelectField
from wtforms.validators import required
from project import app, db
from flask import redirect, url_for, request, flash
from project.models import User
################
#### config ####
################

main_blueprint = Blueprint('main', __name__,)


################
#### routes ####
################

@main_blueprint.route('/')
@login_required
def home():
    return render_template('main/index.html')


@main_blueprint.route('/showusers', methods=['GET', 'POST'])
@login_required
def showusers():
  if not current_user.admin:
    return redirect('/')
  users = User.query.all()
  return render_template("main/Users.html", users=users)


@main_blueprint.route('/api/filldetails', methods=['GET', 'POST'])
def filldetails():
  if request.headers['Content-Type'] == 'application/json':
    user = User.query.filter_by(user_token = request.json['token']).first()
    data = {}
    if user :
      user.mobileno = request.json['mobileno']
      user.latitude = request.json['lat']
      user.longitude = request.json['lon']
      user.contacts = request.json['contacts']
      user.gcmid  = request.json['gcmid']
        # if request.json['token'] == 
      db.session.commit()
      data['response'] = "success"  
      return json.dumps(data)
    else:
      data['response'] = "failure"  
      return json.dumps(data)


@main_blueprint.route('/api/getdetails', methods=['GET', 'POST'])
def getdetails():
  if request.headers['Content-Type'] == 'application/json':
    user = User.query.filter_by(user_token = request.json['token']).first()
    data = {}
    if user :
      data['email'] = user.email
      data['name'] = user.name
      data['mobileno'] = user.mobileno
      data['lat'] = user.latitude
      data['lon'] = user.longitude
      data['contacts'] = user.contacts
      data['gcmid'] = user.gcmid
      data['response'] = "success"
      return json.dumps(data)
    else:
      data['response'] = "failure"
      return json.dumps(data)

import urllib, json
@main_blueprint.route('/api/weather', methods=['GET', 'POST'])
def weather():
  api_key = "f3d7d2bc7eef02d1a59d6217dc182120"
  if request.headers['Content-Type'] == 'application/json':
    lat = request.json['lat']
    lon = request.json['lon']
    if lat and lon:
      url = "http://api.openweathermap.org/data/2.5/weather?lat="+ lat +"&lon="+ lon +"&appid=" + api_key
      print url
      response = urllib.urlopen(url)
      data = json.loads(response.read())
      resp = {}
      if data['cod'] == 200:
        resp['response'] = "success"
        resp['word'] = data['weather'][0]['main']
        resp['icon'] = data['weather'][0]['icon']
        resp['temp'] = data['main']['temp']
        resp['humi'] = data['main']['humidity']

        return json.dumps(resp)
      else:
        resp['response'] = "failure"
        return json.dumps(resp)

from math import radians, cos, sin, asin, sqrt
def dis(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    km = 6367 * c
    return km

@main_blueprint.route('/pushnotif', methods=['GET', 'POST'])
def pushnotif():
  if current_user.admin:
    impact = request.args.get('impact')
    precaution = request.args.get('precaution')
    serverlat = request.args.get('serverlat')
    serverlon = request.args.get('serverlon')
    users = User.query.all()
    for user in users:
      if user.longitude and user.latitude and serverlon and serverlat:
        current_dis = dis(float(user.longitude), float(user.latitude), float(serverlon), float(serverlat))
        # flash(current_user, "warning")
        if current_dis < float(impact):
          user.threat = True
          user.precaution = precaution
          db.session.commit()
  return render_template('main/push.html')

@main_blueprint.route('/api/pushnotif', methods=['GET', 'POST'])
def apipushnotif():
  if request.headers['Content-Type'] == 'application/json':
    user = User.query.filter_by(user_token = request.json['token']).first()
    if user:
      data = {}
      if user.threat:
        data['response'] = 1
        data['precaution'] = user.precaution
        return json.dumps(data)
      else:
        data['response'] = 0
        return json.dumps(data)


from flask.ext.mail import Message
from project import app, mail

@main_blueprint.route('/api/emergency', methods=['GET', 'POST'])
def emergency():
  if request.headers['Content-Type'] == 'application/json':
    user = User.query.filter_by(user_token = request.json['token']).first()
    # user = User.query.first()
    data = {}
    if user:
      lat = request.json['lat']
      lon = request.json['lon']
      if lat and lon:
        listo = user.contacts.split(',')
        # listo = "me@himanshugautam.com, himanshu81494@gmail.com".split(', ')
        subject = "Hi,"+user.email+"is in danger"
        template = "<a href='https://www.google.co.in/maps/@%s,%s,15z' >Locate %s!</a>"%(lat, lon, user.email)
        msg = Message(
        subject,
        recipients=listo,
        html=template,
        sender=app.config['MAIL_DEFAULT_SENDER']
        )
        if mail.send(msg):
          data['response'] = "success"
          return json.dumps(data)
    else:
      data['response'] = "failure"
      return json.dumps(data)

@main_blueprint.route('/api/toggle', methods=['GET', 'POST'])
def toggle():
  if request.headers['Content-Type'] == 'application/json':
    user = User.query.filter_by(id = request.json['toggle']).first()
    data = {}
    if user:
      if user.threat: 
        user.threat = False
      else:
        user.threat = True
      db.session.commit()
    data['response'] = "success"
    return json.dumps(data)

import httplib
@main_blueprint.route('/api/gcm', methods=['GET', 'POST'])
def gcm():
  data = {}
  if request.headers['Content-Type'] == 'application/json':
    user = User.query.filter_by(user_token = request.json['token']).first()
    if user :

      user.gcmregid = request.json['regId']
      user.gcmapikey = request.json['api_key']
      db.session.commit()
      data['response'] = "success"
      return json.dumps(data)
    else:
      data['response'] = "failure"
      return json.dumps(data)

'''
from gcm import *
@main_blueprint.route('/api/test', methods=['GET', 'POST'])
def test():
  # https://www.digitalocean.com/community/tutorials/how-to-create-a-server-to-send-push-notifications-with-gcm-to-android-devices-using-python
  data = {}
  gcm = GCM("AIzaSyCOV9NF0aE1yDc3SXp8_UwnnfmFpcRA3-c")
  message = {}
  message['Notification'] = "Push Notification"
  # message['type'] = "NOTIFICATION_DISASTER"
  message['title'] = "Emergency Notification"
  message['subtitle'] = "gcm demo"
  message['tickerText'] = "ticker"
  message['vibrate'] = 2
  message['sound'] = 3
    
  
  reg_id = "APA91bGcILcvKarkKKYfSUYGPYae0gh6lqypVCeLY0kwvqbn98jBilCYQ_HH3O69CCq63pkKfXMv8Gubo_xNvHQ7-BqrIipfuMwF6vkQFnUibeAFVgkbjhbz2313A-A-aoUZDfz3-VPU"
  response = gcm.plaintext_request(registration_id=reg_id, data = message)
  
  return json.dumps(message)
'''


"""
  regtoken = "APA91bGcILcvKarkKKYfSUYGPYae0gh6lqypVCeLY0kwvqbn98jBilCYQ_HH3O69CCq63pkKfXMv8Gubo_xNvHQ7-BqrIipfuMwF6vkQFnUibeAFVgkbjhbz2313A-A-aoUZDfz3-VPU"
  apikey = "AIzaSyDrvGfB9D1t6WJPfOiZ1swauKo7NQ7-rm0"
  message = {}
  message['Notification'] = "Push Notification"
  message['type'] = "NOTIFICATION_DISASTER"
  message['title'] = "Emergency Notification"
  message['subtitle'] = "gcm demo"
  message['tickerText'] = "ticker"
  message['vibrate'] = 2
  message['sound'] = 3
    
  fields = {}
  fields['registration_ids'] = regtoken
  fields['data'] = message


  headers = {"Content-type": "application/json", "Authorization": "key="+apikey }
  Url = "android.googleapis.com/gcm/send"
  conn = httplib.HTTPConnection(Url)
  conn.request("POST", "", fields, headers)
  response = conn.getresponse()
  return response


"""