import zmq

#set up the PULL receiveer socket
context = zmq.Context()
receiver = context.socket(zmq.PULL)
receiver.connect("tcp://localhost:5557")

#set up the subscriber socket
subscriber = context.socket(zmq.SUB)
subscriber.connect("tcp://localhost:5556")
subscriber.setsockopt(zmq.SUBSCRIBE, b"1001")

#   Set up a poll set, register the two sockets as incoming??
poller = zmq.Poller()
poller.register(receiver, zmq.POLLIN)
poller.register(subscriber, zmq.POLLIN)


while True:

    try:
        socks = dict(poller.poll())

    except KeyboardInterrupt:
        break

    if receiver in socks:
        message = receiver.recv()
        #Do something with the message

    if subscriber in socks:
        message - subscriber.recv()
        # Process weather update

