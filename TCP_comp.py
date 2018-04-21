import sys
import socket
import traceback

BUFFER_SIZE = 4096
MESSAGE = "exit"

try:
    ip_address = sys.argv[1]
    port_number = int(sys.argv[2])
except:
    traceback.print_exc()
    raise Exception("Error occurred while reading parameters")

while (1):
    expression = str(input("enter command: "))
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip_address, port_number))
    except socket.error:
        raise Exception("Client was unable to connect to Server")
    try:
        print("sending to ip address " + ip_address + " and port number " + str(port_number))
        s.send(expression)
    except socket.error:
        raise Exception("Client was unable to send message to Server")