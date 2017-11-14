from __future__ import print_function
import multiprocessing
import zmq

NBR_CLIENTS = 10 
NBR_WORKERS = 3

#   Requests work to be done to the broker, the broker forwards this to the worker
def client_task(identity):

    #   Request-Reply client using a REQ socket
    socket = zmq.Context().socket(zmq.REQ)
    socket.identity = u"client-{}".format(identity).encode("ascii")
    socket.connect("ipc://frontend.ipc")

    #   send the request, wait for the response, print the address and the reply
    socket.send(b"HELLO")
    reply = socket.recv()
    print("{}: {}".format(socket.identity.decode("ascii"), reply.decode("ascii")))

#   This receives a request forwarded through the broker from the client to do some work

def worker_task(identity):

    #   Worker task, uses a REQ socket to do load-balancing.
    socket = zmq.Context().socket(zmq.REQ)
    socket.identity = u"Worker-{}".format(identity).encode("ascii")
    socket.connect("ipc://backend.ipc")

    #   send a message to say that this worker is ready for work
    socket.send(b"READY")

    #   receive the requests, send back - using the address from the req, with an ok message
    while True:
        address, empty, request = socket.recv_multipart()

        print("{}: {}".format(socket.identity.decode("ascii"),request.decode("ascii")))

        socket.send_multipart([address, b"", b"OK"])


def main():

    context = zmq.Context.instance()
    #   frontend router
    frontend = context.socket(zmq.ROUTER)
    frontend.bind("ipc://frontend.ipc")
    #    backend router
    backend = context.socket(zmq.ROUTER)
    backend.bind("ipc://backend.ipc")

    #   SETTING UP PROCESSES
    def start(task, *args):
        process = multiprocessing.Process(target=task, args=args)
        process.daemon = True
        process.start()
    
    #   Start the client tasks as a new process
    for i in range(NBR_CLIENTS):
        start(client_task, i)
    #    start the workers as a new process
    for i in range(NBR_WORKERS):
        start(worker_task, i)

    
    #   Main Loop for distrbuting messages
    count = NBR_CLIENTS
    workers = []
    poller = zmq.Poller()

    #   register requests from the backend
    poller.register(backend, zmq.POLLIN)

    while True:

        sockets = dict(poller.poll())

        #   if its an input from the backend
        if backend in sockets:
            #   receive the request process the first 3 elements
            request = backend.recv_multipart()
            worker, empty, client = request[:3]

            #   if workers is empty, add the frontend to the poller
            if not workers:
                poller.register(frontend, zmq.POLLIN)

            #   add the worker to the list of workers
            workers.append(worker)
            #   if the response wasnt ready - process the rest of the response?
            if client != b"READY" and len(request) > 3:
                empty, reply = request[3:]
                frontend.send_multipart([client, b"", reply])
                count -= 1
                if not count:
                    break

        if frontend in sockets:
            client, empty, request = frontend.recv_multipart()
            print("frontend coms: %s" % request)
            worker = workers.pop(0)
            backend.send_multipart([worker, b"", client, b"", request])
            if not workers:
                poller.unregister(frontend)

    # Clean up
    backend.close()
    frontend.close()
    context.term()

if __name__ == "__main__":
    main()
