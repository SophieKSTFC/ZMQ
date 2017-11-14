import zmq 
import sys

DEFAULT = 10

def main():

    if len(sys.argv) > 1:
        SUBS_EXPECTED = int(sys.argv[1])
    else: 
        SUBS_EXPECTED = DEFAULT
 
    # define the context, create a publisher socket, set the high water mark and bind to port 5561
    context = zmq.Context()
    publisher = context.socket(zmq.PUB)
    publisher.sndhwm = 1100000
    publisher.bind("tcp://*:5561")
       
    # create a REPLY socket and bind it to port 5562
    synchro = context.socket(zmq.REP)
    synchro.bind("tcp://*:5562")

    # flag to determine whether we need to continue getting subscribers
    get_subs = True
    nbr_subs = 0
    while get_subs:
        # send out a call to subs
        publisher.send(b"hello?")
        try:
            #check for a message, this will not block
            message = synchro.recv(flags=zmq.NOBLOCK)
            #a message has been received
            nbr_subs += 1
            print ("Sending no. %i subcriber request acknowledgement..." % nbr_subs)
            synchro.send_string("Thanks, you are subscriber - %i" % nbr_subs)
            if nbr_subs == SUBS_EXPECTED:
                get_subs = False
                break
        #if there was no message....
        except zmq.Again as e:
            print ("No further response, currently operating with (%i / %i) subscriber(s)" % (nbr_subs, SUBS_EXPECTED))
            continue
        #if we interrupted - close subs/sockets and context cleanly 
        except KeyboardInterrupt:
            print("  Interrupt received, stopping..")
            publisher.send(b"FAIL")
            synchro.close()
            publisher.close()
            context.term()
            print("Program Quit")

    # once we have the right number of subs
    if not get_subs:
        # send a ready request to synchronise them all
        publisher.send(b'Ready')
        #send out a real data
        for i in range(1000000):
            publisher.send(b'Rhubarb')
        # once we're done - end the transmission
        publisher.send(b"END")
        print("Transmission complete with %i subscribers" % nbr_subs)


if __name__ == '__main__':
    main()