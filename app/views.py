from app import app, socketio, thread
import time
from threading import Thread
from flask import render_template, session, request
from flask.ext.socketio import emit, join_room, leave_room, \
    close_room, rooms, disconnect
import json

def background_thread():
    count = 0

@app.route('/')
def index():
    global thread
    if thread is None:
        thread = Thread(target=background_thread)
        thread.daemon = True
        thread.start()
    return render_template('index.html')

@socketio.on("map update", namespace="/test")
def map_update(coords):
    coords = coords["data"]
    uid, lat, lon = coords['uid'], coords["lat"], coords["lon"]
    if "map_coords" in session:
        """ This either updates or adds a new user and his/her info. """
        session["map_coords"][uid] = {"uid": uid, "lat": lat, "lon": lon}
    else:
        """ Set up a new map_coords session (first step) """
        session["map_coords"] = {}
        session["map_coords"][uid] = {"uid": uid, "lat": lat, "lon": lon}
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

    if "map_coords" in session:
        """ This either updates or adds a new user and his/her info. """
        session["map_coords"][uid] = {"uid": uid, "lat": lat, "lon": lon}
    else:
        """ Set up a new map_coords session (first step) """
        session["map_coords"] = {}
        session["map_coords"][uid] = {"uid": uid, "lat": lat, "lon": lon}

    print session["map_coords"][uid]

@socketio.on('connect', namespace='/test')
def test_connect():
    emit('my response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)
