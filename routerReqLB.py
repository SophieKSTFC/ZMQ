#
#   Sends out 100 workloads, balanced across the 10 workers
#   Each worker gives a ready status once it's done each work
#   The router distributes the workload to the first worker to send the ready
#




import zmq
import random
from threading import Thread
import time
import zhelpers

NBR_WORKERS = 10

def worker_thread(context=None):

    context = context or zmq.Context.instance()
    worker = context.socket(zmq.REQ)

    zhelpers.set_id(worker)
    worker.connect("tcp://localhost:5671")

    total = 0
    while True:
        #    Tell the router we're ready for work
        worker.send(b"ready")

        #   wait for the workload from the router, check if its finished, else add 1 to process
        workload = worker.recv()
        print(workload)
        finished = workload == b"END"
        if finished:
            print("Processed: %d tasks" % total)
            break
        total += 1

        # do the work
        time.sleep(0.1 * random.random())    

#get the context instance and set up a router
context = zmq.Context.instance()
client = context.socket(zmq.ROUTER)
client.bind("tcp://*:5671")

#    start 10 workers
for x in range(NBR_WORKERS):
    Thread(target=worker_thread).start()

#    wait for the ready message, and send a workload back
for n in range(NBR_WORKERS * 10):

    address, empty, ready = client.recv_multipart()

    client.send_multipart([address, b"",b"This is the workload",])

#   receive ready and send the shutdown message
for i in range(NBR_WORKERS):
    address, empty, ready = client.recv_multipart()
    client.send_multipart([address,b"",b"END"])


