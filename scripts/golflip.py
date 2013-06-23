#coding=UTF-8
import socket
import time
import sys
from random import randint
import os
import platform

UDPHOST="2001:7f0:3003:cafe:222:f9ff:fe01:c65"
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

# Game of live from https://github.com/whtsky/Game-of-Life

ALIVE = 1
DEAD = 0
SIZE_Y = 16
SIZE_X = 40
RANDOM = 4
DELAY = 20

REALIVE = 3
MAX = 4
MIN = 1

assert 8>=MAX>=REALIVE>=MIN>=0

def init_table():
    return [([(ALIVE if randint(0,100) <= RANDOM else DEAD) for x in xrange(SIZE_X)]) for x in xrange(SIZE_Y)]

def aref2(y, x):
    if y >= SIZE_Y or y < 0:
        return 0;
    if x >= SIZE_X or x < 0:
        return 0;
    return table[y][x]

def next():
    changes = 0
    for y in xrange(SIZE_Y):
        for x in xrange(SIZE_X):
            cell = table[y][x]
            livenum = -cell
            for n in (y+1,y,y-1):
                for m in (x-1,x,x+1):
                    livenum += aref2(n, m);

            if cell is ALIVE and (livenum <= MIN or livenum >= MAX):
                if table[y][x] == ALIVE: changes += 1
                table[y][x] = DEAD
            elif livenum == REALIVE:
                if table[y][x] == DEAD: changes += 1
                table[y][x] = ALIVE
    return changes

def sendgol():
	frame = []
	for line in table:
		frame.append([1 if x == 0 else 0 for x in line])
	print frame
	send(frame)
	time.sleep(DELAY)

def show():
    for y in xrange(SIZE_Y):
        for x in xrange(SIZE_X):
            if table[y][x] is ALIVE:
                print ' ',
            else:
                print '█',
        print ''

table = init_table()
while True:
    os.system("clear")
    show()
    sendgol()
    changes = next()
    if changes == 0:
        table = init_table()
    time.sleep(DELAY)
