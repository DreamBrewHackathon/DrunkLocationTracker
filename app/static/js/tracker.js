// GLOBAL VARS //

// Labels for Map Markers
var labels = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
var labelIndex = 0;

// Google map object
var map = null;

// Marker store
var markerStore = [];

// Users
var users = {};

// Random id generated when first connecting
// List of possible ids
var ids = [..."ABCDEFGHIJKLMNOPQRSTUVWXYZ"];

// Get random character
var rand_id = ids[Math.floor(Math.random() * ids.length)];

// User id based on initials
var initials;

// Counter that keeps track of number of times zoomed
var zoom_counter = 0;

// Initialize map
function initMap() {
  var mapOptions = {
    center: new google.maps.LatLng(1.3, 103.8),
    zoom: 11,
    mapTypeId: google.maps.MapTypeId.ROADMAP
  };
  map = new google.maps.Map(document.getElementById("map-canvas"),
                                    mapOptions);
}

google.maps.event.addDomListener(window, 'load', initMap);

// Reset the map
function resetMap() {
  map = null;
  var mapOptions = {
    center: new google.maps.LatLng(0, 0),
    zoom: 2,
    mapTypeId: google.maps.MapTypeId.ROADMAP
  };
  map = new google.maps.Map(document.getElementById("map-canvas"), mapOptions);
  google.maps.event.addDomListener(window, 'load', initMap);
}

// This can be used to reset the map as well
function setMapOnAll(map) {
  for (var i = 0; i < markerStore.length; i++) {
    markerStore[i].setMap(map);
  }
}

// Add a marker
function addMarker(map_coords, label, from_users) {
  var lat;
  var lon;

  if (from_users) {
    lat = map_coords.lat;
    lon = map_coords.lon;
  } else {
    lat = map_coords.data.lat;
    lon = map_coords.data.lon;
  }

  var latLong = new google.maps.LatLng(lat, lon);
  var marker = new google.maps.Marker({
      position: latLong,
      label: label
  });
  marker.setMap(map);

  if (zoom_counter === 0){
    map.setZoom(15);
    zoom_counter++;
  }

  if (!from_users) {
    map.setCenter(marker.getPosition());
  }

  markerStore.push(marker);
}

// Updates map using all coordinates in the user dictionary.
function initMapWithCoords() {
  // First reset map
  setMapOnAll(null);

  var marker;

  // Call addMarker for each user in users
  // Create a marker for each user in users
  for (var user in users) {
    console.log(user);
    console.log(users[user]["lat"] + " " + users[user]["lon"]);

    marker = new google.maps.Marker({
      position: new google.maps.LatLng(users[user]["lat"], users[user]["lon"]),
      map: map,
      label: users[user]["uid"]
    });
    markerStore.push(marker);

    if (users[user]["uid"] === initials) {
      map.setCenter(marker.getPosition());
    }

    if (zoom_counter === 0){
      map.setZoom(15);
      zoom_counter++;
    }

    console.log("Called");
  }
}

namespace = '/test'; // change to an empty string to use the global namespace

// the socket.io documentation recommends sending an explicit package upon connection
// this is specially important when using the global namespace
var socket = io.connect('http://' + document.domain + ':' + location.port + namespace);

$(document).ready(function(){

    // event handler for server sent data
    // the data is displayed in the "Received" section of the page
    socket.on('my response', function(msg) {
        // $('#log').append('<br>Received #' + msg.count + ': ' + msg.data);
    });

    // event handler for server sent data for newly updated/added location.
    socket.on("map update", function(coords) {
        // add the uid to session if not already done so
        socket.emit("add uid and coords", coords);

        // add the user and coords to local dictionary
        if (!users.hasOwnProperty(coords.data.uid)) {
          $("#log").append("<br>Name: " + coords.data.name + ", Number: " + "<a href='tel:" + coords.data.number + "'>" + coords.data.number + "</a>" + ", Address: " + coords.data.address);
        }

        users[coords.data.uid] = {"name": coords.data.name, "number": coords.data.number, "address": coords.data.address, "uid": coords.data.uid,
        "lat": coords.data.lat, "lon": coords.data.lon};

        console.log(users);

        initMapWithCoords();

        // $("#log").append("<br>Received lat/lon/uid: " + coords.data.lat + ", " + coords.data.lon + ", " + coords.data.uid);
    });

    // event handler for new connections
    socket.on('connect', function() {
        socket.emit('my event', {data: 'I\'m connected!'});
    });


    window.setInterval(function() {
      printLocation();
    }, 5000);
});

function printLocation() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(showPosition);
  }
};

function showPosition(position) {
  // For testing - vary the marker position with each call.

  var random_lat = Math.random()/100;
  var random_lon = Math.random()/100;

  // add your location to the map
  /*
  coords = {
    "data": {
      "lat": position.coords.latitude + random_lat,
      "lon": position.coords.longitude + random_lon
    }
  }
  */

  coords = {
    "data": {
      "lat": position.coords.latitude,
      "lon": position.coords.longitude
    }
  }

  // user id is based on user initials
  initials = "{{initials}}"

  // Broadcast your location
  socket.emit("map update", {data: {"name": "{{name}}", "number": "{{number}}", "address": "{{address}}", "uid": initials,
  "lat": position.coords.latitude, "lon": position.coords.longitude } });
};
