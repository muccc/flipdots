#coding=UTF-8
import socket
import time
import sys
# from random import randint
# import os
# import platform
import math

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

COLS = 40
ROWS = 16

def make_buffer(cols, rows):
    return [[0 for i in range(cols)] for j in range(rows)]

def draw_sine(image, scale, offset, freq, phase):
    for col in range(COLS):
        x = (col-COLS/2.0)/100.0
        y = math.sin(x*freq+phase)
        target_row = round(y*scale + offset)
        print target_row
        for row in range(ROWS):
            if target_row == row:
                image[row][col] = 1
    return image

def main(dt):
    scale = 8-1/16
    f = 5.0
    offset = ROWS/2-1
    phase = 0
    dphase = 0.01
    while True:
        image = make_buffer(COLS, ROWS)
        draw_sine(image, scale, offset, f, phase)
        send(image)
        phase += dphase/dt
        time.sleep(dt)

FPS = 15.0
main(1/FPS)
