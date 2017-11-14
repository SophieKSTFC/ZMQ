import zmq
import zhelpers

context = zmq.Context()

# Router to process the messages
sink = context.socket(zmq.ROUTER)
sink.bind("inproc://example")

# anonymous socket that will get a random identity assigned
anon = context.socket(zmq.DEALER)
anon.connect("inproc://example")
anon.send(b"Router uses a generated 5 byte identity")
zhelpers.dump(sink)

# socket which will have a predefined identity
identified = context.socket(zmq.DEALER)
identified.setsockopt(zmq.IDENTITY, b"PEER2")
identified.connect("inproc://example")
identified.send(b"ROUTER socket uses REQ's socket identity")
zhelpers.dump(sink)