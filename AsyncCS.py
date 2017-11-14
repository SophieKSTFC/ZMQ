import zmq
import sys
import threading
import time
from random import randint, random

def tprint(msg):
    sys.stdout.write(msg + "\n")
    sys.stdout.flush()

class Client_Task(threading.Thread):

    def __init__(self, id):
        self.id = id
        threading.Thread.__init__(self)
    
    def run(self):
        context = zmq.Context()
        socket = context.socket(zmq.DEALER)
        identity = u"worker-%d" % self.id
        socket.identity = identity.encode("ascii")
        socket.connect("tcp://localhost:5570")

        print("Client %s started" % (identity))
        poll = zmq.Poller()
        poll.register(socket, zmq.POLLIN)

        reqs = 0
        while True:
            reqs += 1
            print("Req %d sent.. " % reqs)
            socket.send_string(u'request #%d' % reqs)
            for i in range(5):
                sockets = dict(poll.poll(1000))
                if socket in sockets:
                    msg = socket.recv()
                    tprint("Clients %s received: %s" % (identity, msg))
        
        socket.close()
        context.term()
        
class ServerTask(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
    
    def run(self):
        context = zmq.Context()
        frontend = context.socket(zmq.ROUTER)
        frontend.bind("tcp://*:5570")

        backend = context.socket(zmq.DEALER)
        backend.bind("inproc://backend")

        workers = []

        for i in range(5):
            worker = ServerWorker(context)
            worker.start()
            workers.append(worker)
        
        zmq.proxy(frontend, backend)

        frontend.close()
        backend.close()
        context.term()
       
class ServerWorker(threading.Thread):

    def __init__(self, context):
        threading.Thread.__init__(self)
        self.context = context

    def run(self):
        worker = self.context.socket(zmq.DEALER)
        worker.connect('inproc://backend')
        tprint("Worker started")

        while True:
            identity, msg = worker.recv_multipart()
            tprint("Worker received %s from %s" % (msg, identity))
            replies = randint(0, 4)
            for i in range(replies):
                time.sleep(1. / (randint(1, 10)))
                worker.send_multipart([identity, msg])
        worker.close()

def main():
    server = ServerTask()
    server.start()
    for i in range(3):
        client = Client_Task(i)
        client.start()

    #    block untill this thread stops
    server.join()

if __name__ == "__main__":
    main()