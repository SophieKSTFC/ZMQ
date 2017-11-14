#
#   Task ventilator - binds a PUSH socket to tcp localhost 5557
#   Sends batch of tasks to workers via that socket
#
#

import zmq
import random
import time

try: 
    raw_input
except NameError:
    raw_input = input

context = zmq.Context()

#this is the socket to send worker messages on
sender = context.socket(zmq.PUSH)
sender.bind("tcp://*:5557")

#this socket has direct access to the sink - used to syncho the start of the batch
sink = context.socket(zmq.PUSH)
sink.connect("tcp://localhost:5558")

print("Press enter when the workers are ready: ")
_ = raw_input()
print("Sending tasks to workers...")

# 1st message is 0 - signals the start of the batch
sink.send(b'0')

#initialise random number gen
random.seed()

#send 100 tasks
total_msec = 0
for task_nbr in range(100):

    workload = random.randint(1, 100)
    total_msec += workload
    sender.send_string(u'%i' % workload)

print("Total expected cost: %s msec" % total_msec)

#give timne to deliver
time.sleep(1)