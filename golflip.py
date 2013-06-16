#coding=UTF-8
import socket
import time
import sys
from random import randint
import os
import platform

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
		msg += chr(int(str(i[::-1]), 2))
	
	sock.sendto(msg, (UDPHOST, UDPPORT))

# Game of live from https://github.com/whtsky/Game-of-Life

ALIVE = 1
DEAD = 0
SIZE = 16
RANDOM = 50
DAILY = 0.5

REALIVE = 3
MAX = 4
MIN = 1

assert 8>=MAX>=REALIVE>=MIN>=0

table = [([(ALIVE if randint(0,100) <= RANDOM else DEAD) for x in xrange(SIZE)]) for x in xrange(SIZE)]

def next():
    for x in xrange(SIZE):
        for y in xrange(SIZE):
            cell = table[x][y]
            livenum = -cell
            for m in (x+1,x,x-1):
                for n in (y-1,y,y+1):
                    livenum += table[m % SIZE][n % SIZE]

            if cell is ALIVE and (livenum <= MIN or livenum >= MAX):
                table[x][y] = DEAD
            elif livenum == REALIVE:
                table[x][y] = ALIVE

def sendgol():
	send([([1] * 40) * 16])
	frame = []
	for line in table:
		frame.append(([1] * 12) + [1 if x == 0 else 0 for x in line] + ([1] * 12))
	print frame
	send(frame)
	time.sleep(1)

def show():
    for x in xrange(SIZE):
        for y in xrange(SIZE):
            if table[x][y] is ALIVE:
                print ' ',
            else:
                print '█',
        print ''

while True:
    os.system("clear")
    show()
    sendgol()
    next()
    time.sleep(DAILY)

