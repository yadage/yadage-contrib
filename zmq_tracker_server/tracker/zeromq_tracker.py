import zmq
import time
import json
from yadage.helpers import WithJsonRefEncoder


class ZeroMQTracker(object):
    def __init__(self,socket = None, connect_string = None, identifier = 'yadage'):
        self.identifier = identifier
        self.socket = socket

    def initialize(self,adageobj):
        self.socket.send_json({'yadage_ctrl': 'clear', 'identifier': 'default'})
        self.track(adageobj)

    def track(self,adageobj):
        serialized = json.dumps(adageobj.json(), cls=WithJsonRefEncoder, sort_keys=True)
        self.socket.send_json({'yadage_obj': json.loads(serialized), 'identifier': self.identifier})

    def finalize(self,adageobj):
        self.track(adageobj)
