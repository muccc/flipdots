#!env python
# -*- coding: utf-8 -*-
#
# Python Snake Game
#
# Usage:
#
# arrow keys to change direction
# n to play on the next host of UDPHOSTS
# s for statistics: apples eaten / highscore \n steps moved
# p for pause
#
#
# Map files are json objects with the keys "dir" and "board"
#  "dir": direction vector
#  "board": array of strings in the matrix dimension
#    currently supported bytes: 'W', ' ', '0'
#    ' ': no wall
#    'W': wall
#    '0': part of the body of player 0
#    other integers are reserved for mutliplayer support
#    currently the snake can't be wrapped around the borders
#
# settings are stored in a file settings
# if this file doesn't exist, it will be created with default settings
# delete the file if new versions have new settings
#
# To reset highscore $ mosquitto_pub -h test.mosquitto.org -t \
# "/de/ccc/muc/flipdot/snake/highscore" -n -r

import socket, time, math
from random import randint
import Image, ImageFont, ImageDraw, sys
import curses
import json
import threading
import atexit

highscore_enabled = True
try:
    import mosquitto
except (NameError, ImportError):
    highscore_enabled = False

# some static settings:
global settings
settings = {
# Game over if the snake head collides into its own body
"COLLIDE_SELF":True,
# Allow to change bearing by 180° (wich will result in a collision if COLLIDE_SELF == True)
"ALLOW_180_DEG_DC":False,
# Collide with the outer borders or wrap around
"WRAP_BORDERS":True,

# List of UDP hosts you can cycle through with n
"UDPHOSTS":["::1","2001:7f0:3003:cafe:222:f9ff:fe01:c65","2001:7f0:3003:cafe:4be:6b21:90c7:fbd9"],
# Frames per second
"FPS": 10,
# map to load, filename must exist in directory lvl/SIZE_X_SIZE_Y/
"MAP": "classic"
}

udphostc=0
UDPPORT=2323

SIZE_Y = 16
SIZE_X = 40

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

    sock.sendto(msg, (settings["UDPHOSTS"][udphostc], UDPPORT))

def save_settings():
    fd = open('settings',"w")
    json.dump(settings,fd,indent=2)

def load_settings():
    global settings
    try:
        settings = json.load(open('settings','r'))
    except IOError:
        save_settings()

load_settings()
lvl = json.load(open('lvl/%i_%i/%s' % (SIZE_X,SIZE_Y,settings["MAP"]),'r'))
buf = [([ PX[1] if lvl["board"][y][x] == "W" else PX[0] for x in xrange(SIZE_X)]) for y in xrange(SIZE_Y)]

stats=[0,0]

def set_px(x,y,v):
    buf[x][y] = PX[v]

def set_pxp(p,v):
    buf[p[0]][p[1]] = PX[v]

def exit_game():
    save_settings()
    sys.exit()

def show_stats():
    send(str2image(str(stats[0])+"/"+str(highscore))[0:SIZE_Y/2] + str2image(str(stats[1]))[0:SIZE_Y/2] )

def game_over(score, highscore):
    show_stats()
    if highscore < score and highscore_enabled:
        mqttc.publish(MQTT_HIGHSCORE_PATH, score, retain=True)
    exit_game()

# Mqtt message obtained. This will always get a message as the
# highscore topic is published with retain=True
def on_message(mosq, obj, msg):
    global highscore # makes it shared
    highscore = int(msg.payload)

def init_snk():
    x,y = 0,0
    snk=[]
    for line in lvl["board"]:
        for c in line:
            if "0" == c: # the level format indicates 0 as body for player 0, so currently only 1 player is supported
                print x,y
                snk.append([y,x])
            x+=1
        x=0
        y+=1
    return snk

def main(win):
    curses.use_default_colors()
    global udphostc
    global stats
    win.nodelay(True) # make getkey() not wait
    b = tuple(lvl["dir"])
    food = (0,[0,0])
    snk = init_snk()

    for p in snk:
       set_px(p[0], p[1], 1)  # paint the snake into the buffer

    nextpop = False

    global stdscr
    stdscr = curses.initscr()
    paused = False

    if highscore_enabled:
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
        try:
            key = win.getkey()
        except: # in no delay mode getkey raise and exeption if no key is press 
            key = None
        if key == "KEY_DOWN" and not (b == (-1,0) and not settings["ALLOW_180_DEG_DC"]):
            b = (1,0)
        elif key == "KEY_UP" and not (b == (1,0) and not settings["ALLOW_180_DEG_DC"]):
            b = (-1,0)
        elif key == "KEY_RIGHT" and not (b == (0,-1) and not settings["ALLOW_180_DEG_DC"]):
            b = (0,1)
        elif key == "KEY_LEFT" and not (b == (0,1) and not settings["ALLOW_180_DEG_DC"]):
            b = (0,-1)
        elif "n" == key:
            udphostc=(udphostc+1) % len(settings["UDPHOSTS"])
        elif "q" == key:
            game_over(stats[0], highscore)
        elif "s" == key:
            show_stats()
            time.sleep(1)
        elif "p" == key:
            paused = not paused

        if paused:
            continue

        stats[1] += 1

        # place a piece of food if the choosen coordinates are free
        if randint(0,100) > 50 and 0 == food[0]:
            food = (1,[randint(0,SIZE_Y-1),randint(0,SIZE_X-1)])
            if food[1] in snk or "W" == lvl["board"][food[1][0]][food[1][1]]:
                food = (0,(0,0))

        if nextpop == True:
            nextpop == False
            #if snk[-1] != snk[0]:
            set_pxp(snk.pop(0),0)

        # eat the food
        if snk[-1] == food[1] and 1 == food[0]:
            stats[0] += 1
            food = (0,(0,0))
            # avoid the impression of stalling while eating
            nextpop = False
        else:
            nextpop = True

        snk += [ map(lambda x, y: x + y, snk[-1], b) ]
        if (settings["WRAP_BORDERS"]):
            snk[-1][0] %= SIZE_Y
            snk[-1][1] %= SIZE_X
        elif snk[-1][0] < 0 or snk[-1][1] < 0 or snk[-1][0] >= SIZE_Y or snk[-1][1] >= SIZE_X:
            game_over(stats[0], highscore)

        # crash into ourself
        if settings["COLLIDE_SELF"] and snk[-1] in snk[0:-1]:
            game_over(stats[0], highscore)

        # render blinkenfood
        if food[0] != 0:
            if stats[1]%4 < 2:
                set_px(food[1][0], food[1][1], 0) # draw food
            else:
                set_px(food[1][0], food[1][1], 1) # draw food

        #seems redundant
        #set_px(snk[0][0], snk[0][1], 0) # remove the tail of the snake
        set_pxp(snk[-1],1)

        # crash into walls
        if "W" == lvl["board"][snk[-1][0]][snk[-1][1]]:
            game_over(stats[0],highscore)

        send(buf)
        time.sleep(1.0/settings["FPS"])

#a wrapper to create a window, and clean up at the end
curses.wrapper(main)

