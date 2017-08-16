#!/usr/bin/env python3
from time import sleep
from pygame.locals import *
import pygame
import socket

UDP_HOST="::1"
UDP_PORT=5555

def sendCommand(s, player_id, command):
    s.sendto(bytearray([ord(x) for x in player_id] + [ord(" ")] + [ord(x) for x in command.upper()]),
            (UDP_HOST,UDP_PORT))

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
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            c1 = "left"
        elif keys[K_RIGHT]:
            c1 = "right"
        elif keys[K_UP]:
            c1 = "up"
        elif keys[K_DOWN]:
            c1 = "down"
        if keys[K_w]:
            c2 = "up"
        elif keys[K_a]:
            c2 = "left"
        elif keys[K_s]:
            c2 = "down"
        elif keys[K_d]:
            c2 = "right"
        pygame.event.pump()
        sendCommand(s, "derp", c1)
        sendCommand(s, "durp", c2)
        sleep(.01)

if __name__ == "__main__":
    pygameInputHandler()
