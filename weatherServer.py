#
#   Weather update server, binds PUB socket to tcp://*:5556
#   Publishes random weather updates
#


from random import randrange
import zmq

context = zmq.Context()
socket = context.socket(zmq.PUB) #make a publisher socket
socket.bind("tcp://*:5556")

while True:

    zipcode = randrange(1, 100000)
    temp = randrange(-80, 135)
    relHumidity = randrange(10, 60)

    socket.send_string("%i %i %i" % (zipcode, temp, relHumidity))