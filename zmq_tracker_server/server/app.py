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
    socket.connect('ipc://../what.sock')
    socket.setsockopt_string(zmq.SUBSCRIBE,u'')
    while True:
        msg = socket.recv_json()
        if 'yadage_ctrl' in msg:
            sio.emit('yadage_ctrl', {'data': msg['yadage_ctrl']}, namespace='/test')    
        elif 'yadage_obj' in msg:
            sio.emit('yadage_state', {'data': msg['yadage_obj']}, namespace='/test')

@app.route('/')
def index():
    return render_template('index.html')

@sio.on('frontendmessage', namespace='/test')
def test_message(sid, message):
    sio.emit('servermessage', {'data': message['data']}, room=sid, namespace='/test')

@sio.on('connect', namespace='/test')
def test_connect(sid, environ):
    sio.emit('servermessage', {'data': 'Connected', 'count': 0}, room=sid, namespace='/test')


@sio.on('disconnect', namespace='/test')
def test_disconnect(sid):
    print('Client disconnected')

if __name__ == '__main__':
    sio.start_background_task(background_thread)
    pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler).serve_forever()


