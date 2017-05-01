#!/usr/bin/env python2
from time import sleep
from pygame.locals import *
import pygame
import socket

def sendCommand(s, player_id, command):
    s.sendto("%s %s" % (player_id, command.upper()), ("2001:7f0:3003:235f:ba9a:3c03:185d:69b5",5555))

def pygameInputHandler():
    pygame.init()
    screen = pygame.display.set_mode((10,10))
    pygame.display.set_caption("FlipPong")
    pygame.mouse.set_visible(0)
    pygame.key.set_repeat(1,1)
    s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)

    while True:
        c1 = "none"
        c2 = "none"
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_LEFT:
                    c1 = "left"
                elif event.key == K_RIGHT:
                    c1 = "right"
                elif event.key == K_UP:
                    c1 = "up"
                elif event.key == K_DOWN:
                    c1 = "down"
                elif event.key == K_w:
                    c2 = "up"
                elif event.key == K_a:
                    c2 = "left"
                elif event.key == K_s:
                    c2 = "down"
                elif event.key == K_d:
                    c2 = "right"
        sendCommand(s, "derp", c1)
        sendCommand(s, "durp", c2)
        sleep(.01)

if __name__ == "__main__":
    pygameInputHandler()
