#
#   Request- reply client connects a REQ to localhost 5559
#   sends hello to the server and expects world back
#

import zmq

context = zmq.Context()
socket = context.socket(zmq.REQ)

socket.connect("tcp://localhost:5559")

for request in range(1, 11):
    socket.send(b"Hello")
    message = socket.recv()
    print("Received reply %s [%s]" %(request, message))
