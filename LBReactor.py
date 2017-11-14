from __future__ import print_function

import threading
import time
import zmq

''' non blocking event I/O allows resources to be accessed whilst an event doesnt rely on x being completed. '''
from zmq.eventloop.ioloop import IOLoop 
from zmq.eventloop.zmqstream import ZMQStream  #registers call backs when sockets send or receive messages


NBR_CLIENTS = 10
NBR_WORKERS = 3

#   Sends out a ready message status through the backend socket to the broker, waits for a reply from a client, "works" then replies
def worker_thread(worker_url, i):
    
    context = zmq.Context.instance()
    socket = context.socket(zmq.REQ)

    #   Give the socket an identity
    socket.identity = (u"Worker-%d" % (i)).encode("ascii")

    #   connect to the backend
    socket.connect(worker_url)
    #   send ready status
    socket.send(b"READY")

    try:
        while True:
            #   strip the client address, delim and message (HELLO).
            address, empty, request = socket.recv_multipart()

            print("Worker received : %s: %s\n" % (socket.identity.decode("ascii"), 
                                                    request.decode("ascii")), end="")

            #   send back an OK message to the same client address
            socket.send_multipart([address, b"", b"OK"])
    #   exit cleanly
    except zmq.ContextTerminated:
        return

#   Client thread, sends out hello message asking for work to be done, waits for a reply. Single use client
def client_thread(client_url, i):

    context = zmq.Context.instance()
    socket = context.socket(zmq.REQ)

    socket.identity = (u"Client-%d" % (i)).encode("ascii")
    #   connect to the frontend
    socket.connect(client_url)

    socket.send(b"HELLO")
    reply = socket.recv()

    print("Client received this reply: %s: %s\n" % (socket.identity.decode("ascii"), reply.decode("ascii")), end="")

class LRUQueue(object):

    def __init__(self, backend_socket, frontend_socket):
        self.available_workers = 0
        self.workers = []
        self.client_nbr = NBR_CLIENTS

        #   Use a stream to enable callback methods for the frontend and backend sockets
        self.backend = ZMQStream(backend_socket)
        self.frontend = ZMQStream(frontend_socket)

        #   Set up to call handle_backend when we receive input on the backend socket (we dont care about frontend untill we have workers registered)
        self.backend.on_recv(self.handle_backend)

        self.loop = IOLoop.instance()
    
    def handle_backend(self, msg):

        #   split the multipart 
        worker_addr, empty, client_addr = msg[:3]

        #   ensure that we have worker spaces left
        assert self.available_workers < NBR_WORKERS

        #   Add the worker who just contacted us
        self.available_workers += 1
        self.workers.append(worker_addr)

        #   If it was NOT a READY status message we need to forward this onto a client
        if client_addr != b"READY":
            #   get the rest of the message which would be 5 parts (workerID, , client_ID, , OK)
            empty, reply = msg[3:]
            assert empty == b""
            #   send on the reply (OK) to the client address 
            self.frontend.send_multipart([client_addr, b"", reply])

            #   We've just serviced a client so remove that from the number of clients
            self.client_nbr -= 1

            #   When we run out of client services, wait 1 second and then close the loop cleanly
            if self.client_nbr == 0:
                self.loop.add_timeout(time.time() + 1, self.loop.stop)

        #   If it was a READY message and the first worker to register, start accepting messages + processing callbacks from the frontend
        if self.available_workers == 1:
            self.frontend.on_recv(self.handle_frontend)

    def handle_frontend(self, msg):

        #   the new client message i.e HELLO
        client_addr, empty, request = msg

        assert empty == b""

        #   new request from a client so we are going to use a worker, -1 worker and get the least recently used worker ID
        self.available_workers -= 1
        worker_id = self.workers.pop()     

        #   send the new work (HELLO) onto the LRU worker 
        self.backend.send_multipart([worker_id, b"", client_addr, b"", request])

        #   If we have no available workers, stop receiving frontend requests
        if self.available_workers == 0:
            self.frontend.stop_on_recv() 

def main():

    #   Create IPC urls
    url_worker = "ipc://backend.ipc"
    url_client = "ipc://frontend.ipc"

    #   bind frontend and backend sockets
    context = zmq.Context()
    frontend = context.socket(zmq.ROUTER)
    frontend.bind(url_client)

    backend = context.socket(zmq.ROUTER)
    backend.bind(url_worker)

    #   create n worker threads
    for i in range(NBR_WORKERS):
        thread = threading.Thread(target=worker_thread, args=(url_worker, i, ))
        thread.daemon = True
        thread.start()

    #   create n client threads
    for i in range(NBR_CLIENTS):
        thread_c = threading.Thread(target=client_thread, args=(url_client, i, ))
        thread_c.daemon = True
        thread_c.start()
    
    #   set up the queue to process callbacks on both sockets
    queue = LRUQueue(backend, frontend)

    #   start the IO loop
    IOLoop.instance().start()

if __name__ == "__main__":
    main()