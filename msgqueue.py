#
#   Simple req and reply broker for message queuing by using a proxy
#
#

import zmq

def main():

    context = zmq.Context()

    frontend = context.socket(zmq.ROUTER)
    frontend.bind("tcp://*:5559")

    backend = context.socket(zmq.DEALER)
    backend.bind("tcp://*:5560")

    # this replaces the RRBroker in 1 line. - checks if theres a message from front end, if so sends it to back end
    zmq.proxy(frontend, backend)

    frontend.close()
    backend.close()
    context.term()

if __name__ == "__main__":
    main()