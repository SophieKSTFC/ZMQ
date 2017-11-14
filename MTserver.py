import time
import threading
import zmq

# this gets called every time we make a new thread
# creates a new context instance and a new REPLY socket connected to the worker URL
# receives messages from the clients and responds


def worker_routine(worker_url, number, context=None):

    context = context or zmq.Context.instance()

    socket = context.socket(zmq.REP)
    socket.connect(worker_url)

    while True:

        string = socket.recv()
        print("operating on thread [%d]received request: [%s]" % (number, string))

        #do some 'work'
        time.sleep(1)

        #reply
        socket.send(b"World")

def main():

    #set up a url for the workers (servers) - this is internal process not a communication line socket
    url_worker = "inproc://workers"

    #set the url for the clients - hwclient.py
    url_client = "tcp://*:5555"

    context = zmq.Context.instance()

    #set up a router socket for the clients 
    clients = context.socket(zmq.ROUTER)
    clients.bind(url_client)

    # set up a dealer socket for the workers
    workers = context.socket(zmq.DEALER)
    workers.bind(url_worker)

    # create a set of threads
    for i in range(5):
        print("Creating thread %d" % i)
        #each thread - call the worker routine method with the arguments
        thread = threading.Thread(target=worker_routine, args=(url_worker,i, ))    
        thread.start()

    # set up the REPREQ
    # communications between the client server coming in and the workers
    zmq.proxy(clients, workers)

    clients.close()
    workers.close()
    context.term()

if __name__ == "__main__":
    main()