
import time
import random
from threading import Thread
import zmq

def worker_a(context=None):

    context = context or zmq.Context.instance()
    worker = context.socket(zmq.DEALER)
    worker.setsockopt(zmq.IDENTITY, b"A")
    worker.connect("ipc://routing.ipc")

    total = 0
    while True:
        #   receive the workload
        request = worker.recv()
        print(request)
        finished = request == b"END"
        if finished:
            print("A received: %s" % total)
            break
        total +=1

def worker_b(context=None):

    context = context or zmq.Context.instance()
    worker = context.socket(zmq.DEALER)
    worker.setsockopt(zmq.IDENTITY, b"B")
    worker.connect("ipc://routing.ipc")

    total = 0
    while True:
        #   receive the workload
        request = worker.recv()
        print(request)
        finished = request == b"END"
        if finished:
            print("B received: %s" % total)
            break
        total +=1


context = zmq.Context.instance()
client = context.socket(zmq.ROUTER)
client.bind("ipc://routing.ipc")

Thread(target=worker_a).start()
Thread(target=worker_b).start()

time.sleep(1)

for x in range(10):

    #   Choose an address to send the work to, unbalanced favour to A
    ident = random.choice([b'A', b'A', b'B'])
    #   format the workload message
    work = b"This is the workload"
    #    send the multipart message
    client.send_multipart([ident, work])

client.send_multipart([b'A', b'END'])
client.send_multipart([b'B', b'END'])
