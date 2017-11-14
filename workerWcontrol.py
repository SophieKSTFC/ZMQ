#
#   Task worker, connects a PULL socket to 5557
#   Collects workloads from the ventilator from 5557
#   Connects a PUSH socket to 5558 (Sink)
#   Sends the sink the message via 5558
#   Subscribes to the sinks PUB -> if receives control message- worker dies.
#   Includes a poller to handle the messages from both sockets


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

#subscribe to the sinks control messages
controller = context.socket(zmq.SUB)
controller.connect("tcp://localhost:5559")
controller.setsockopt(zmq.SUBSCRIBE, b'')

# process messages from both the receiver (ventilator) and the sink
poller = zmq.Poller()
poller.register(receiver, zmq.POLLIN)
poller.register(controller, zmq.POLLIN)


#   process the tasks 
while True:

    socks = dict(poller.poll())

    # if we get messages from the reciver.. do the work
    if socks.get(receiver) == zmq.POLLIN:

        message = receiver.recv_string()
        workload = int(message)

        # do the work
        time.sleep(workload / 1000.0)
        #send the results to the sink (5558)
        sender.send_string(message)
         #   Simple progress indicator for the viewer - forces the buffer to be written to the terminal
        sys.stdout.write('.')
        sys.stdout.flush()

    # if we get messages from the controller - stop 
    if socks.get(controller) == zmq.POLLIN:
        break

receiver.close()
sender.close()
controller.close()
context.term()
