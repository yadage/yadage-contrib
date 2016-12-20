This snippet provides two things:

* a ZeroMQ tracker that sends the JSON serialized version of the yadage object over the wire
* a server that subscribes to messages sent over the wire and pushes them via socket.io to a frontend

