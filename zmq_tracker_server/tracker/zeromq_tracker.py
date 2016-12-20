import zmq
import time
import json
from yadage.helpers import WithJsonRefEncoder

ctx = zmq.Context()

class ZeroMQTracker(object):
    def __init__(self,connect_string):
        self.socket = ctx.socket(zmq.PUB)
        self.socket.bind(connect_string)

    def initialize(self,adageobj):
        self.track(adageobj)

    def track(self,adageobj):
        serialized = json.dumps(adageobj.json(), cls=WithJsonRefEncoder, sort_keys=True)
        self.socket.send_json(json.loads(serialized))

    def finalize(self,adageobj):
        self.track(adageobj)
