import socket
import sys

server_address = ('localhost', 4141)

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
print ('connecting to %s port %s' % server_address)
sock.connect(server_address)

while(1):
    print(sock.recvmsg().decode('utf-8'))