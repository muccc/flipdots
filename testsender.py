import socket
import time

#UDPHOST="2001:a60:2458:f001:222:f9ff:fe01:c65"
UDPHOST="fe80::222:f9ff:fe01:c65%wlan0"
UDPPORT=2323
UDPPORT=2704

sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)

def send(value):
  msg = chr(value)*((16*40)/8)
  sock.sendto(msg, (UDPHOST, UDPPORT))

v = 0
while 1:
    send(v)
    v+=1
    time.sleep(.4)
