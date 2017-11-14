#
#   Broker - connects a REQ and REP b/t a client and server
#
#

import zmq

context = zmq.Context()

#clients connect to the router
frontend = context.socket(zmq.ROUTER)
# servers connect to the dealer
backend = context.socket(zmq.DEALER)

#bind the sockets to the ports which the server and the client are connected to
frontend.bind("tcp://*:5559")
backend.bind("tcp://*:5560")

poller = zmq.Poller()
poller.register(frontend, zmq.POLLIN)
poller.register(backend, zmq.POLLIN)

while True:

    socks = dict(poller.poll())

    if socks.get(frontend) == zmq.POLLIN:
        message = frontend.recv_multipart()
        backend.send_multipart(message)

    if socks.get(backend) == zmq.POLLIN:
        message = backend.recv_multipart()
        frontend.send_multipart(message)