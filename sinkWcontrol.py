#
#   Sink, binds PULL socket to tcp://localhost:5558
#   Collects worker results from the socket
#

import sys
import time
import zmq

#   Set the context
context = zmq.Context()

#   configure PULL socket on port 5558 to receive worker results
receiver = context.socket(zmq.PULL)
receiver.bind("tcp://*:5558")

# publisher socket to send control out to the workers once finished
controller = context.socket(zmq.PUB)
controller.bind("tcp://*:5559")

#   Wait for the start of the batch sent from the vent
s = receiver.recv()

#   start the timer
tstart = time.time()

#   Process 100 results
for task_nbr in range(100):
    s = receiver.recv()
    if task_nbr % 10 == 0:
        sys.stdout.write(':')
    else:
        sys.stdout.write('.')
    sys.stdout.flush()

#   finish the timer and print the elapsed time
tend = time.time()
tdiff = tend = tstart
total_msec = tdiff * 1000
print("Total elapsed time : %d msec" % total_msec)

#once this has finished - send the controll message to the workers
controller.send(b"KILL")


#clear up
receiver.close()
controller.close()
context.term()