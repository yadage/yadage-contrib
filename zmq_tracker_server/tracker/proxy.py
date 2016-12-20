import zmq
ctx = zmq.Context()


backend  = ctx.socket(zmq.XSUB)
backend.bind('ipc://backend.sock')

frontend  = ctx.socket(zmq.XPUB)
frontend.bind('ipc://frontend.sock')

proxy = zmq.proxy(frontend, backend)
