import socket
import time
import sys
import random

UDPHOST="fe80::222:f9ff:fe01:c65%eth0"
UDPPORT=2323

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

invaders = [
		[
			[
				[1,1,0,1,1,1,1,1,1,1,0,1,1],
				[1,1,1,0,1,1,1,1,1,0,1,1,1],
				[1,1,0,0,0,0,0,0,0,0,0,1,1],
				[1,0,0,1,0,0,0,0,0,1,0,0,1],
				[0,0,0,0,0,0,0,0,0,0,0,0,0],
				[0,1,0,0,0,0,0,0,0,0,0,1,0],
				[0,1,0,1,1,1,1,1,1,1,0,1,0],
				[1,1,1,0,0,0,1,0,0,0,1,1,1],
			],
			[
				[1,1,0,1,1,1,1,1,1,1,0,1,1],
				[0,1,1,0,1,1,1,1,1,0,1,1,0],
				[0,1,0,0,0,0,0,0,0,0,0,1,0],
				[0,0,0,1,0,0,0,0,0,1,0,0,0],
				[1,0,0,0,0,0,0,0,0,0,0,0,1],
				[1,0,0,0,0,0,0,0,0,0,0,0,1],
				[1,1,0,1,1,1,1,1,1,1,0,1,1],
				[1,0,1,1,1,1,1,1,1,1,1,0,1],
			],
		],
		[
			[
				[1,1,1,1,0,0,0,0,1,1,1,1],
				[1,0,0,0,0,0,0,0,0,0,0,1],
				[0,0,0,0,0,0,0,0,0,0,0,0],
				[0,0,0,1,1,0,0,1,1,0,0,0],
				[0,0,0,0,0,0,0,0,0,0,0,0],
				[1,1,1,0,0,1,1,0,0,1,1,1],
				[1,1,0,0,1,0,0,1,0,0,1,1],
				[0,0,1,1,1,1,1,1,1,1,0,0],
			],
			[
				[1,1,1,1,0,0,0,0,1,1,1,1],
				[1,0,0,0,0,0,0,0,0,0,0,1],
				[0,0,0,0,0,0,0,0,0,0,0,0],
				[0,0,0,1,1,0,0,1,1,0,0,0],
				[0,0,0,0,0,0,0,0,0,0,0,0],
				[1,1,1,0,0,1,1,0,0,1,1,1],
				[1,1,0,0,1,0,0,1,0,0,1,1],
				[1,0,0,1,1,1,1,1,1,0,0,1],
			],
		],
		[
			[
				[1,1,1,0,0,1,1,1],
				[1,1,0,0,0,0,1,1],
				[1,0,0,0,0,0,0,1],
				[0,0,1,0,0,1,0,0],
				[0,0,0,0,0,0,0,0],
				[1,1,0,1,1,0,1,1],
				[1,0,1,0,0,1,0,1],
				[0,1,0,1,1,0,1,0],
			],
			[
				[1,1,1,0,0,1,1,1],
				[1,1,0,0,0,0,1,1],
				[1,0,0,0,0,0,0,1],
				[0,0,1,0,0,1,0,0],
				[0,0,0,0,0,0,0,0],
				[1,1,0,1,1,0,1,1],
				[1,0,1,1,1,1,0,1],
				[1,1,0,1,1,0,1,1],
			],

		],
	]

while True:
	invader = random.randrange(0, len(invaders))

	preframe = []
	postframe = []
	preframe += ([[1] * 40] * random.randrange(0, 16 - len(invaders[invader][0]), 1))
	postframe += ([[1] * 40] * (16 - len(preframe) - len(invaders[invader][0])))
	leftspace = 1
	
	while leftspace < (40 - len(invaders[invader][0][0])):
		frame = []
		frame += preframe
		showframe = leftspace % 2
		for line in invaders[invader][showframe]:
			theline = [1] * leftspace
			theline += line
			theline += [1] * (40 - len(theline))
			frame.append(theline)
		frame += postframe
		#print frame
		send(frame)
		time.sleep(0.1)
		leftspace += 1

