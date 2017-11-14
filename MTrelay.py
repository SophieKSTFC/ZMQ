import threading
import zmq


#this step is the last thread to get started at the top of stream, it then sends down the messages back down the line
def step1(context=None):

    context = context or zmq.Context.instance()
    # set up a sender socket, send a message back down to step 2
    sender = context.socket(zmq.PAIR)
    sender.connect("inproc://step2")
    sender.send_string("BAM")

def step2(context=None):

    context = context or zmq.Context.instance()

    #this is to receive the message from step1
    receiver = context.socket(zmq.PAIR)
    receiver.bind("inproc://step2")

    #start step 1
    thread = threading.Thread(target=step1)
    thread.start()

    # receive the string message
    msg = receiver.recv_string()
    print("step 1 ready")

    # send the message on to step 3
    sender = context.socket(zmq.PAIR)
    sender.connect("inproc://step3")
    sender.send_string(msg)

def main():

    context = zmq.Context.instance()

    # socket to receive the message from step2
    receiver = context.socket(zmq.PAIR)
    receiver.bind("inproc://step3")
   

    #start step 2 thread
    thread = threading.Thread(target=step2)
    thread.start()
    # receive the message from step 2
    string = receiver.recv_string()
    print("step 2 ready")
    # print and close
    print("Test successful!" + string) 
    print("step 3 complete")

    receiver.close()
    context.term()

if __name__ == "__main__":
    main()