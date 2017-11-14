#
#   Hello world server - PYTHON
#   Binds REP socket to tcp://*:5555
#   Expects b"hello" from client, replies with b"World"
#

import zmq
import time
import msgpack
import datetime
from _ipc_message import IpcMessage, IpcMessageException
from zmq.utils.strtypes import unicode, cast_bytes


context = zmq.Context()

#bind a reply socket to port 5555
socket = context.socket(zmq.REP) 
socket.bind("tcp://*:5555") #opens a ZeroMQ socket on port 5555

while True:

    #   Wait for next request from client
    request = socket.recv()
    request = IpcMessage(from_str=request)
    print("received request : %s." % request)

    #message = umsgpack.unpackb(message)
    #print("Received request: %s" % message)

    #   Do something

    time.sleep(1)

    data = request.get_param("DATA")
    type_ = str(type(data))
    print("---\n")
    print(data)
    print(type_)
    print("\n---")

   


    reply_string = "Internal Error"
    reply_message = IpcMessage(msg_type="CMD", msg_val="NOTIFY")
    reply = "Received"

    reply_string = "Processed Request. %s" % (reply)
    reply_message.set_param("REPLY", reply_string)
    reply_message = reply_message.encode()
                    

    if isinstance(reply_message, unicode):
        reply_message = cast_bytes(reply_message)

    socket.send(reply_message)
