import zmq

def main():

    #   Subcriber number provided by the publisher
    sub_Num = None

    #   create the context and a subscriber socket, connect to the port, subscribe to all
    context = zmq.Context()
    subscriber = context.socket(zmq.SUB)
    subscriber.connect("tcp://localhost:5561")
    subscriber.setsockopt(zmq.SUBSCRIBE, b'')

    #   Set the acknowledged flag to false ( we have no ACK'd yet) and wait for a message from the Publisher
    ACK = False
    msg = subscriber.recv()

    #   connect to the req-rep socket/port
    synchro = context.socket(zmq.REQ)
    synchro.connect("tcp://localhost:5562")
    
    #   Respond to a hello message, ack the SUB subscription
    while not ACK:
        if msg == b'hello?':
            print("Request to subscribe received, subscribing...")
            #    send a response back
            synchro.send(b'')
            #   receive the subscription number acknowledgment 
            msg = synchro.recv_string()
            sub_Num = (msg.split("-")[1]).strip()
            print("Subscriber %s confirming join" % sub_Num)
            ACK = True

    
    receive_data = False
    data_num = -1

    #   Now SUB is legitimatle subscribed, receive publish messsages
    while ACK:
        msg = subscriber.recv()
        #    check for the ready signal, if the pub has all the subs it will send this message first to synchro sub late joiners
        if msg == b'Ready':
            print("Subscriber %s ready to receive" % sub_Num)
            receive_data = True
        if msg == b'FAIL':
            if data_num == -1:
                data_num = 0
            print("Subscriber %s received %d updates succesfully. Subscriber failing securely.." % (sub_Num, data_num))
            subscriber.close()
            synchro.close()
            context.term()
            break
        #   check if the end signal is set, if so break and clean up
        if msg == b'END':
            #     parting messsages and cleaning up
            print("Subscriber %s : End of transmission received..." % sub_Num)
            print("Subscriber %s received %d updates succesfully" % (sub_Num,data_num))
            subscriber.close()
            synchro.close()
            context.term()  
            print("Goodbye")
            break
        #   process the data in synchro with any other subs
        if receive_data:
            data_num += 1

if __name__ == '__main__':
    main()
