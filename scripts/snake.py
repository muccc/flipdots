#!env python
# -*- coding: utf-8 -*-
#
# Snake Game
# 
# Use arrow keys to change direction and n to play on the next host
#
# To reset highscore $ mosquitto_pub -h test.mosquitto.org -t \
# "/de/ccc/muc/flipdot/snake/highscore" -n -r

import socket, time, math
from random import randint
import Image, ImageFont, ImageDraw, sys
import curses
import mosquitto
import threading
import atexit

# some static settings:
settings = {
# Game over if the snake head collides into its own body
"COLLIDE_SELF":True,
# Allow to change bearing by 180° (wich will result in a collision if COLLIDE_SELF == True)
"ALLOW_180_DEG_BC":False,
# Collide with the outer borders or wrap around
"WRAP_BORDERS":True,
}

UDPHOSTS=["::1","2001:7f0:3003:cafe:222:f9ff:fe01:c65","2001:7f0:3003:cafe:4be:6b21:90c7:fbd9"]
UDPHOSTC=0
UDPPORT=2323

SIZE_Y = 16
SIZE_X = 40
FPS = 10

PX = (0,1) # white-on-black = (0,1), black-on-white = (1,0)

FONT_SIZE = 8
FONT_OFFSET= (1, -1)

MQTT_HIGHSCORE_PATH = "/de/ccc/muc/flipdot/snake/highscore/"
MQTT_CLIENT_ID = 'de.ccc.muc.flipdot.snake'

# This is filled with the highscore obtained via MQTT
global highscore
highscore = 0

sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)

class MqttLoop(threading.Thread):
    def __init__(self, mqtt_client):
        threading.Thread.__init__(self) 
        self.client = mqtt_client

    def run(self):
        while True:
            self.client.loop()

def str2image(s):
    image = Image.new("1", (SIZE_X, SIZE_Y), PX[0])
    draw = ImageDraw.Draw(image)
    draw.fontmode = "1"         # No AA
    font = ImageFont.load_default()
    # font = ImageFont.truetype("FreeSans.ttf", FONT_SIZE)

    draw.text(FONT_OFFSET, s, font=font, fill=PX[1])

    imgmap = []
    for pixel in image.getdata():
        imgmap.append(pixel)

    return [imgmap[i*SIZE_X:i*SIZE_X+SIZE_X] for i in range(len(imgmap)/SIZE_X)]


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
	
    sock.sendto(msg, (UDPHOSTS[UDPHOSTC], UDPPORT))

buf = [([ PX[0]  for x in xrange(SIZE_X)]) for x in xrange(SIZE_Y)]
stats=[0,0]

def set_px(x,y,v):
    buf[x][y] = PX[v]

def set_pxp(p,v):
    buf[p[0]][p[1]] = PX[v]

def exit_game():
    sys.exit()
    
def game_over(score, highscore):
    if highscore < score:
        mqttc.publish(MQTT_HIGHSCORE_PATH, score, retain=True)
        send(str2image("HS "+str(stats[0])))
    else:
        send(str2image("no HS"))
    exit_game()

# Mqtt message obtained. This will always get a message as the
# highscore topic is published with retain=True
def on_message(mosq, obj, msg):
    global highscore # makes it shared
    highscore = int(msg.payload)

def main(win):
    global UDPHOSTC
    global stats
    win.nodelay(True) # make getkey() not wait
    b = (1,1)
    food = (0,[0,0])
    snk = [[3,5],[3,6],[3,7],[3,8]]
    for p in snk:
       set_px(p[0], p[1], 1)  # paint the snake into the buffer
    nextpop = False

    global stdscr
    stdscr = curses.initscr()

    global mqttc
    global mqtt_loop
    mqttc = mosquitto.Mosquitto(MQTT_CLIENT_ID, clean_session = True)
    mqttc.connect("test.mosquitto.org")
    mqttc.on_message = on_message
    mqttc.subscribe(MQTT_HIGHSCORE_PATH)
    mqtt_loop = MqttLoop(mqttc)
    mqtt_loop.setDaemon(True)
    mqtt_loop.start()

    while True:
        stats[1] += 1
        try:
            key = win.getkey()
        except: # in no delay mode getkey raise and exeption if no key is press 
            key = None
        if key == "KEY_DOWN" and not (b == (-1,0) and not settings["ALLOW_180_DEG_BC"]):
            b = (1,0)
        elif key == "KEY_UP" and not (b == (1,0) and not settings["ALLOW_180_DEG_BC"]):
            b = (-1,0)
        elif key == "KEY_RIGHT" and not (b == (0,-1) and not settings["ALLOW_180_DEG_BC"]):
            b = (0,1)
        elif key == "KEY_LEFT" and not (b == (0,1) and not settings["ALLOW_180_DEG_BC"]):
            b = (0,-1)
        elif key == "n":
            UDPHOSTC=(UDPHOSTC+1) % len(UDPHOSTS)
        elif key == "q":
            exit_game()

        # place a piece of food if the choosen coordinates are free
        if randint(0,100) > 50 and food[0] == 0:
            food = (1,[randint(0,SIZE_Y-1),randint(0,SIZE_X-1)])
            if food[1] in snk:
                food = (0,(0,0))
            else:
                set_px(food[1][0], food[1][1], 1) # draw food

        if nextpop == True:
            nextpop == False
            set_pxp(snk.pop(0),0)

        # eat the food
        if snk[-1] == food[1] and food[0] == 1:
            stats[0] += 1
            food = (0,(0,0))
            # avoid the impression of stalling while eating
            nextpop = False
        else:
            nextpop = True

        # crash into ourself
        if settings["COLLIDE_SELF"] and snk[-1] in snk[0:-1]:
            game_over(stats[0], highscore)

        snk += [ map(lambda x, y: x + y, snk[-1], b) ]
        if (settings["WRAP_BORDERS"]):
            snk[-1][0] %= SIZE_Y
            snk[-1][1] %= SIZE_X
        elif snk[-1][0] < 0 or snk[-1][1] < 0 or snk[-1][0] >= SIZE_Y or snk[-1][1] >= SIZE_X:
            game_over(stats[0], highscore)
        set_pxp(snk[-1],1)
        set_px(snk[0][0], snk[0][1], 0) # remove the tail of the snake

        send(buf)
        time.sleep(1.0/FPS)

#a wrapper to create a window, and clean up at the end
curses.wrapper(main)

