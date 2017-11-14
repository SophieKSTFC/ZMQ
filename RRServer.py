#
#   RR server, expects hello from client replies with world
#
#

import zmq

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.connect("tcp://localhost:5560")

while True:
    message = socket.recv()
    print("Receiver request: %s" % message)
    socket.send(b"World")