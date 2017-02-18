import socket, time, math
from random import randint

#UDPHOST="2001:7f0:3003:cafe:222:f9ff:fe01:c65"
UDPHOST="::1"
UDPPORT=2323

SIZE_Y = 16
SIZE_X = 40
FPS = 15
SPEED = 0.8

sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)

def send(image):
	msg = '';
	pieces = '';
	for line in image:
		pieces += ''.join(str(x) for x in line)

	pieces = [pieces[i:i+8] for i in range(0, len(pieces), 8)]

	for i in pieces:
		if (len(i) < 8):
			i = i.ljust(8, '1')
		msg += chr(int(str(i), 2))
	
	sock.sendto(msg, (UDPHOST, UDPPORT))

def make_buffer(thres):
    return [([(1 if randint(0,100) > thres else 0) for x in xrange(SIZE_X)]) for x in xrange(SIZE_Y)]

def main():
    i = 0
    while True:
        THRES = 100*(0.5*math.sin(i/(SPEED*3.14))+0.5)
        send(make_buffer(THRES))
        time.sleep(1.0/FPS)
        print THRES

        i += 1

main()
