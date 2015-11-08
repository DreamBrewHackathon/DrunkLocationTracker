from app import app, socketio, thread
import time
from threading import Thread
from flask import render_template, session, request, redirect, url_for
from flask.ext.socketio import emit, join_room, leave_room, \
    close_room, rooms, disconnect
import json
import uuid

import boto
from boto.s3.key import Key
import os

from config import *

# Boto setup
acc_key = AWS_ACCESS_KEY
acc_sec = AWS_SECRET_KEY
bucket = "partyingsalesman"

# Connect to s3
c = boto.connect_s3(acc_key, acc_sec)
b = c.get_bucket(bucket)
bucket_key = Key(b)

path = "app/static/json/names.json"
map_coords = []

def background_thread():
    count = 0

def get_addresses_from_s3():
    """ Get addresses from s3 """
    bucket_key.key = "names.json"

    map_coords = []
    with open(path, "w+") as fp:
        bucket_key.get_file(fp)
        fp.seek(0)
        map_coords = json.load(fp)
        fp.close()

    return map_coords

def write_to_s3(coords):
    """ Write coordinates to json in s3 """
    bucket_key.key = "names.json"

    map_coords = []
    with open(path, "w+") as fp:
        bucket_key.get_file(fp)
        fp.seek(0)
        map_coords = json.load(fp)
        fp.close()

    map_coords.append(coords)

    # now write to s3
    with open(path, "w+") as fp:
        fp.write(json.dumps(map_coords))
        fp.close()

    # Upload
    bucket_key.set_contents_from_filename(path)

def clear_s3_json():
    """ Clear the json in s3. Called when new session is created. """
    bucket_key.key = "names.json"
    empty = []

    with open(path, "w+") as fp:
        fp.write(json.dumps(empty))
        fp.close()

    # Upload
    bucket_key.set_contents_from_filename(path)
    print "Success"

@app.route("/")
def splash():
    clear_s3_json()
    return render_template("splash.html")

@app.route("/create_room", methods=["GET", "POST"])
def create_room():
    # First, clear json
    namespace = str(uuid.uuid4())
    if request.method=="POST":
        return redirect(url_for('connect'))
    return render_template("create_room.html", namespace=namespace)

@app.route("/connect", methods=["GET", "POST"])
def connect():
    if request.method=="POST":
        name = request.form["name"]
        number = request.form["number"]
        address = request.form["address"]
        return redirect(url_for('map', name=name, number=number, address=address))
    else:
        return render_template("formdetails.html")

@app.route("/sobrietytest")
def sobrietytest():
    return render_template("sobrietytest.html")

@app.route("/drive_home")
def drive_home():
    return render_template("drivehome.html")

@app.route('/map/<name>/<number>/<address>')
def map(name, number, address):
    global thread
    if thread is None:
        thread = Thread(target=background_thread)
        thread.daemon = True
        thread.start()
    name_parts = name.split()
    initials = name_parts[0][0] + name_parts[-1][0]
    return render_template('index.html', initials=initials, name=name, number=number, address=address)

@socketio.on("map update", namespace="/test")
def map_update(coords):
    coords = coords["data"]
    uid, lat, lon, = coords['uid'], coords["lat"], coords["lon"]
    name, number, address = coords["name"], coords["number"], coords["address"]
    if "map_coords" in session:
        """ This either updates or adds a new user and his/her info. """
        session["map_coords"][uid] = coords
        map_coords = session["map_coords"]
    else:
        """ Set up a new map_coords session (first step) """
        session["map_coords"] = {}
        session["map_coords"][uid] = coords
        map_coords = session["map_coords"]
    emit("map update",
        {"data": session["map_coords"][uid]},
        broadcast=True)

@socketio.on("add uid and coords", namespace="/test")
def add_uid_and_coords(coords):
    """ This is for when others join the map. """
    coords = coords["data"]
    print coords.items()

    """ This effectively updates the positions of each person """
    uid, lat, lon = coords["uid"], coords["lat"], coords["lon"]
    name, number, address = coords["name"], coords["number"], coords["address"]

    if "map_coords" in session:
        """ This either updates or adds a new user and his/her info. """
        session["map_coords"][uid] = coords
    else:
        """ Set up a new map_coords session (first step) """
        session["map_coords"] = {}
        session["map_coords"][uid] = coords

    print session["map_coords"][uid]

@socketio.on('connect', namespace='/test')
def test_connect():
    emit('my response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)
