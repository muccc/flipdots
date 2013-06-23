import socket
import time
import sys

UDPHOST="2001:7f0:3003:cafe:222:f9ff:fe01:c65"
UDPPORT=2323

sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)

def send(value):
  msg = chr(value)*((16*40)/8)
  sock.sendto(msg, (UDPHOST, UDPPORT))

v = int(sys.argv[1])
send(v)
