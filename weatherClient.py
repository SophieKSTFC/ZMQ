import sys
import zmq

#   socket to talk to the server
context = zmq.Context()
socket = context.socket(zmq.SUB)

print("collecting updates from the weather server...")
socket.connect("tcp://localhost:5556")

# the zip code filter we are going to use is either passed as the system arguments or 10001 (default)
zip_filter = sys.argv[1] if len(sys.argv) > 1 else "10001"

if isinstance(zip_filter, bytes):
    zip_filter = zip_filter.decode('ascii')

#set a subscription and subscribe else itwont work
socket.setsockopt_string(zmq.SUBSCRIBE, zip_filter)

#process 5 updates and then print out the average of those temperatures
total_temp = 0 
for update_nbr in range(5):
    string = socket.recv_string()
    zipcode, temp, relhumidity = string.split()
    total_temp += int(temp)

print("average temp for zip code '%s' was %dF" % (zip_filter, total_temp / (update_nbr +1)))
