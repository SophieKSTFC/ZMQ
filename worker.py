#
#   Task worker, connects a PULL socket to 5557
#   Collects workloads from the ventilator from 5557
#   Connects a PUSH socket to 5558 (Sink)
#   Sends the sink the message via 5558


import sys
import time
import zmq

context = zmq.Context()

#Socket to receive messages on - connected to the vent
receiver = context.socket(zmq.PULL)
receiver.connect("tcp://localhost:5557")

#   Socket to send the messages to sink
sender = context.socket(zmq.PUSH)
sender.connect("tcp://localhost:5558")

#   process the tasks 
while True:

    s = receiver.recv()

    #   Simple progress indicator for the viewer - forces the buffer to be written to the terminal
    sys.stdout.write('.')
    sys.stdout.flush()

    # do the work
    time.sleep(int(s)* 0.001)

    #send the results to the sink (5558)
    sender.send(b'')
