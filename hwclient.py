# 
#   Hello world client 
#   Connects REQ socket to tcp://localhost:5555
#   sends hello to the server and expects world back
#   

import zmq
import msgpack
import datetime
from _ipc_message import IpcMessage, IpcMessageException
from zmq.utils.strtypes import unicode, cast_bytes
import umsgpack

DATA = [
    -9.223372036854775807, 9.223372036854775807, -9223372036854775807,
    -9223372036854775807, 500, -500, True, False, "Hello", "World", 
    "Really long string here, like honestly who writes this much",
    b'Hello Byte World', b'short', None,
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17],
    {"Key1" : "10", "Key2" : "20", "Key3" : "30", "Key4" : "40"}
    ]




context = zmq.Context() #create a socket

#   Socket to talk to the server
print ("Connecting to hello world server..")
socket = context.socket(zmq.REQ) #request
socket.connect("tcp://localhost:5555")

x = 0
for item in DATA: 

    print("Sending request %d .. " % x)

    request = IpcMessage("CMD", "NOTIFY")
    request.set_param("DEVICE", "CLIENT")
    request.set_param("DATA", item)
    request = request.encode()

    print (request)

    if isinstance(request, unicode):
        print("found unicode\n")
        request = cast_bytes(request)

    socket.send(request)

    

    reply = socket.recv()
    reply = IpcMessage(from_str=reply)
    print("Received Response: %s" % reply.get_param("REPLY"))
    x+=1

"""

#   10 requests, wait each time for a response
for request in range(10):

    #helper function to check what version of zmq we are working on
    print("Current libzmq version is %s" % zmq.zmq_version())
    print("Current  pyzmq version is %s" % zmq.__version__)


    print("Sending request %s .. " % request)

    message = {}
    message['msg_type'] = "CMD"
    message['msg_val'] = "NOTIFY"
    message['timestamp'] = datetime.datetime.now().isoformat()
    message['params'] = {}
    message['params']["DEVICE"] = "SERVER"
    message['params']["MESSAGE"] = "HELLO"

    message = umsgpack.packb(message)
    socket.send(message)

    # Get the reply
    message = socket.recv()
    message = umsgpack.unpackb(message)
    print("Received reply %s [ %s ]" % (request, message))
"""