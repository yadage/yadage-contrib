import zmq
import time
import json
from yadage.helpers import WithJsonRefEncoder

ctx = zmq.Context()

class ZeroMQTracker(object):
    def __init__(self,socket = None, connect_string = None, sleep = 0.0):
        if socket:
            self.socket = socket
        elif connect_string:
            self.socket = ctx.socket(zmq.PUB)
            self.socket.bind(connect_string)
        time.sleep(sleep)

    def initialize(self,adageobj):
        self.socket.send_json({'yadage_ctrl': 'clear'})
        self.track(adageobj)

    def track(self,adageobj):
        serialized = json.dumps(adageobj.json(), cls=WithJsonRefEncoder, sort_keys=True)
        self.socket.send_json({'yadage_obj': json.loads(serialized)})

    def finalize(self,adageobj):
        self.track(adageobj)
