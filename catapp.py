"""
SERVER
LANGUAGES & RESOURCES USED
Python: server-side language. 
Flask SocketIO: for websocket. 
Gevent: to handle streaming Twitter events.
Twython: for streaming Twitter data. Actively maintained, pure Python wrapper for the Twitter API. Supports both normal and streaming Twitter APIs
github.com/djvdorp/Flask-SocketIO-Realtime-Twitter-Stream
flask-socketio.readthedocs.io/en/latest
"""

import gevent
from gevent import monkey; monkey.patch_all()
from flask import Flask
from flask_socketio import SocketIO, emit
import time
from twython import TwythonStreamer

app = Flask(__name__)

#INITIALIZATION
socketio = SocketIO(app)

#Variables that contains the user credentials to access Twitter API 
TOKEN = "1873249183-IFm5ucwZCbYfEynBKs75fZEb3PL6KyoUy2iLXoN"
TOKEN_SECRET = "h5eE8s5fZ9f9oVi4zZTJlVTiYIktv2mAEYNCeF6vwHCdf"
APP_KEY = "AcqegSkFr3qZTHoxqXR2kpbq5"
APP_SECRET = "JXZ1qVXb2zBmx2WaEjTRnRuOxQ9SWNDODBKXBQVF69IldzPmq0"

class TwitterStreamer(TwythonStreamer):
	def __init__(self, *args, **kwargs):
		TwythonStreamer.__init__(self, *args, **kwargs)
        print('Initialized Twitter Streamer')
        self.queue = gevent.queue.Queue()

	def on_success(self, data):
		print('tweet')
		self.queue.put_nowait(data)
		if self.queue.qsize() > 5:
			self.queue.get()

	def on_error(self, status_code, data):
		print('Status code: {status_code}, Data: {data}')
		#stops trying to get data because of the error
		self.disconnect()

class TwitterCatWatch(object):
    def __init__(self):
        self.streamer = TwitterStreamer(APP_KEY, APP_SECRET, TOKEN, TOKEN_SECRET)
        self.green = gevent.spawn(self.streamer.statuses.filter, track='cats')

    def check_alive(self):
        if self.green.dead:
            self.streamer.disconnect()
            self.green.kill()
            self.__init__()

cats = TwitterCatWatch()

#sends html to client. backslash serves index
@app.route('/')
def root():
	#causes index to be sent to client after client enters http://127.0.0.1:5000/ URL into browser. root can take any name
    cats.check_alive()
    return app.send_static_file('index.html')

#on function take message and function parameters. namespaces allow a client to open multiple connections to the server that are multiplexed on a single socket. note: if no namespace included, it uses the incoming message by default as namespace
@socketio.on('connect', namespace='/tweets')
def on_connect():
    print('Connected: {request.namespace.socket.sessid}')
    cats.check_alive()

	#MESSAGES SENT FROM SERVER USING BROADCASTING
	#if broadcast=True optional argument all clients connected to the namespace receive the message. callbacks not invoked for broadcast messages
    while True:
        try:
            tweet = cats.streamer.queue.get(timeout=5)
            text = tweet['text']
            print(text)
            #emit function sends message under a custom event name. alternatively, send function sends message of string or JSON type to the client
            emit('tweet', text, broadcast=True)
        except gevent.queue.Empty:
            cats.check_alive()

@socketio.on('disconnect', namespace='/tweets')
def on_disconnect():
    cats.check_alive()
    print('Disconnected: {request.namespace.socket.sessid}')