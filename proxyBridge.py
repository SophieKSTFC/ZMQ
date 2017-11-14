#
#   Proxy bridge - subscribes to a server in 1 network and publishes it to our own subscribers?
#   Acts like a brideg/ formwarding device between twp different networks/transports
#

import zmq

# Subscribe to the weather server in the other network
frontend = context.socket(zmq.SUB)
frontend.connect("tcp/:/192.168.55.210:5556")

# bind a PUB socket in our own network - subscribers will subscribe to this in our network
backend = context.socket(zmq.PUB)
backend.bind("tcp://10.1.1.0:8100")

#subscribe to everything
frontend.setsockopt(zmq.SUBSCRIBE, b'')

while True:

    #receive the message from the front end (server)
    message = frontend.recv_multipart()

    #send the message on to the network
    backend.send_multipart(message)