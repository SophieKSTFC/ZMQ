import zmq 

#   set the number of expected subscribers
SUBS_EXPECTED = 10

def main():

    # define the context, create a publisher socket, set the high water mark and bind to port 5561
    context = zmq.Context()
    publisher = context.socket(zmq.PUB)
    publisher.sndhwm = 1100000
    publisher.bind("tcp://*:5561")

    # create a REPLY socket and bind it to port 5562
    synchro = context.socket(zmq.REP)
    synchro.bind("tcp://*:5562")

    # whilst there are not 10 subcribers, wait for their message and add a new subscriber
    subs_synched = 0
    while subs_synched < SUBS_EXPECTED:

        msg = synchro.recv()
        synchro.send(b'')
        subs_synched += 1
        print("+1 subscribe (%i/%i)" % (subs_synched, SUBS_EXPECTED))

    #send out a million rhubarbs
    for i in range(1000000):
        publisher.send(b'Rhubarb')

    #send an end message
    publisher.send(b'END')

if __name__ == '__main__':
    main()