import time
import socketio
import zmq.green as zmq
import json
from flask import Flask, render_template
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler

ctx = zmq.Context()
sio = socketio.Server(logger=True, async_mode='gevent')
app = Flask(__name__)
app.wsgi_app = socketio.Middleware(sio, app.wsgi_app)
app.config['SECRET_KEY'] = 'secret!'

def background_thread():
    """Example of how to send server generated events to clients."""
    socket = ctx.socket(zmq.SUB)
    socket.connect('ipc://../tracker/frontend.sock')
    socket.setsockopt_string(zmq.SUBSCRIBE,u'')
    while True:
        msg = socket.recv_json()
        if 'yadage_ctrl' in msg:
            sio.emit('yadage_ctrl', {'data': msg['yadage_ctrl']}, room = msg['identifier'], namespace='/test')    
        elif 'yadage_obj' in msg:
            sio.emit('yadage_state', {'data': msg['yadage_obj']}, room = msg['identifier'], namespace='/test')

@app.route('/<identifier>')
def index(identifier):
    return render_template('index.html', room = identifier)

@sio.on('connect', namespace='/test')
def connect(sid, environ):
    print('Client connected')

@sio.on('join', namespace='/test')
def enter(sid, data):
    print('data',data)
    print('Adding Client {} to room {}'.format(sid, data['room']))
    sio.enter_room(sid, data['room'], namespace = '/test')

@sio.on('roomit', namespace='/test')
def roomit(sid, data):
    print('Emitting to Room: {}'.format(data['room']))
    sio.emit('join_ack', {'data': 'Welcome to the room {}'.format(data['room'])}, room = data['room'], namespace='/test')

@sio.on('disconnect', namespace='/test')
def disconnect(sid):
    print('Client disconnected')

if __name__ == '__main__':
    sio.start_background_task(background_thread)
    pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler).serve_forever()


