from app import app, socketio, thread
import time
from threading import Thread
from flask import render_template, session, request, redirect, url_for
from flask.ext.socketio import emit, join_room, leave_room, \
    close_room, rooms, disconnect
import json
import uuid

def background_thread():
    count = 0

@app.route("/")
def splash():
    return render_template("splash.html")

@app.route("/create_room", methods=["GET", "POST"])
def create_room():
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
    else:
        """ Set up a new map_coords session (first step) """
        session["map_coords"] = {}
        session["map_coords"][uid] = coords
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
