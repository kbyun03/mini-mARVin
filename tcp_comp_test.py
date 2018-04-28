import socket
import math
import sys

TCP_PORT = 12001
BUFFER_SIZE = 4096  # Normally 1024, but we want fast response
try:
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error:
    raise Exception("Failed to create socket")
try:
    hostname = socket.gethostname()
except socket.gaierror:
    raise Exception("Failed to get host name")
try:
    serversocket.bind((hostname, TCP_PORT))
except socket.error:
    raise Exception("Failed to bind socket")
serversocket.listen(5)
while 1:
    conn, addr = serversocket.accept()
    try:
        data = conn.recv(BUFFER_SIZE)
        print(data)
    except:
        raise Exception("Unable to receive data from Client")
