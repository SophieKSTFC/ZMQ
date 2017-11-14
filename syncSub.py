import time
import zmq

def main():

    context = zmq.Context()
    subscriber = context.socket(zmq.SUB)
    subscriber.connect("tcp://localhost:5561")
    subscriber.setsockopt(zmq.SUBSCRIBE, b'')

    time.sleep(1)

    synchro = context.socket(zmq.REQ)
    synchro.connect("tcp://localhost:5562")

    synchro.send(b'')

    synchro.recv()

    nbr = 0
    while True:
        msg = subscriber.recv()
        if msg == b'END':
            break
        nbr += 1

    print("Received %d updates" % nbr)

if __name__ == '__main__':
    main()
