#!/usr/bin/env python2
from FlipdotAPI.FlipdotMatrix import FlipdotMatrix, FlipdotImage
from random import randint
from time import sleep
from threading import Thread
import argparse
import fliputils
import math
import pygame
from pygame.locals import *

class GraphicsObject:
    def __init__(self, x, y, z, sizex, sizey, sizez):
        self.obj_matrix = [[[None for i in range(sizez)] for j in range(sizey)] for k in range(sizex)]
        self.center = (x,y,z)
        self.size = (sizex, sizey, sizez)
        self.fillMatrix()

    def fillMatrix(self):
        self.drawCuboid((0,0,0), self.size)

    def drawCuboid(self, pos, size):
        for z in range(pos[2], pos[2] + size[2]):
            self.drawRectangle((pos[0], pos[1], z),(size[0], size[1]))

    def drawRectangle(self, pos, size):
        for x in range(pos[0], pos[0] + size[0]):
            for y in range(pos[1], pos[1] + size[1]):
                value = 0
                if x == pos[0] or x == pos[0] + size[0] - 1:
                    value = 1
                if y == pos[1] or y == pos[1] + size[1] - 1:
                    value = 1
                self.obj_matrix[x][y][pos[2]] = value

    def lowerLeft(self):
        return (self.center[0]-int(self.size[0]/2),self.center[1]-int(self.size[1]/2),self.center[2]-int(self.size[2]/2))

    def moveZ(self,steps):
        self.center = (self.center[0],self.center[1],self.center[2]+steps)

    def moveX(self, steps):
        self.center = (self.center[0]+steps, self.center[1], self.center[2])

class Car(GraphicsObject):
    def __init__(self, x, y, z, sizex, sizey, sizez = 1):
        GraphicsObject.__init__(self, x, y, z, sizex, sizey, sizez)

    def fillMatrix(self):
        self.drawCuboid((0,0,0), (self.size[0], int(self.size[1]/2), self.size[2]))
        self.drawCuboid((int(self.size[0]/4), int(self.size[1]/2), 0), (int(self.size[0]/2), int(self.size[1]/2), self.size[2]))

class Obstacle(GraphicsObject):
    def __init__(self, x, y, z, sizex, sizey, sizez = 1):
        GraphicsObject.__init__(self, x, y, z, sizex, sizey, sizez)

class Race(Thread):
    def __init__(self, sizex = 144, sizey = 120, speed = 30, udpHostsAndPorts = [], console_out = False, invert = False):
        Thread.__init__(self)
        self.flipmatrix = FlipdotMatrix(udpHostsAndPorts, (sizex, sizey)) if len(udpHostsAndPorts) != 0 else None
        self.sizex = sizex
        self.sizey = sizey
        self.sizez = 100
        self.speed = speed
        self.flipdot_out = len(udpHostsAndPorts) != 0
        self.console_out = console_out
        self.invert = invert
        self.camera = (0, int(self.sizey/3), -int(self.sizez/2))
        self.plain_offset = (-int(self.sizex/2), -int(self.sizey/2))
        self.obstacles = []
        self.car = Car(0, 0, int(self.sizez/4), int(self.sizex/7), int(self.sizey/7))
        self.direction = 0
        self.lost = False
        self.stop = False
        self.pause = False

    def run(self):
        collision = False
        while not collision and not self.stop:
            if self.pause:
                sleep(1./self.speed)
                continue
            collision = self.step()
            image = self.generateRaceImage()
            if self.invert:
                self.invertImage(image)
            if self.flipdot_out:
                flipImage = FlipdotImage(self.transpose(image))
                self.flipmatrix.show(flipImage)
            if self.console_out:
                self.printImage(image)
            sleep(1./self.speed)
        self.lost = True

    def moveRight(self):
        self.direction = +2

    def moveLeft(self):
        self.direction = -2

    def togglePause(self):
        self.pause = not self.pause

    def transpose(self, image):
        new_image = [[0 for x in range(self.sizex)] for y in range(self.sizey)]

        for x in range(self.sizex):
            for y in range(self.sizey):
                new_image[y][x] = image[x][self.sizey - y - 1]

        return new_image

    def invertImage(self, image):
        for i in range(len(image)):
            for j in range(len(image[0])):
                image[i][j] = 0 if image[i][j] else 1

    def printImage(self, image):
        for y in range(len(image[0])-1, -1, -1):
            line = ""
            for x in range(len(image)):
                line += "." if image[x][y] else " "
            print line

    def step(self):
        collision = False
        if randint(0,30) == 0:
            self.obstacles.append(Obstacle(randint(-int(self.sizex/4),int(self.sizex/4)),0,self.sizez, int(self.sizex/7), int(self.sizey/7)))
        self.car.moveX(self.direction)
        self.direction = 0
        remove = []
        for obj in self.obstacles:
            obj.moveZ(-1)
            if self.checkCollision(obj, self.car):
                collision = True
            if obj.center[2] < self.car.center[2]-10:
                remove.append(obj)
        for obj in remove:
            self.obstacles.remove(obj)
        return collision

    def checkCollision(self, obj1, obj2):
        if self.checkCollisionSingleAxis(obj1, obj2, 0) and self.checkCollisionSingleAxis(obj1, obj2, 1) and self.checkCollisionSingleAxis(obj1, obj2, 2):
            return True
        return False

    def checkCollisionSingleAxis(self, obj1, obj2, index):
        obj1pos = obj1.center[index]
        obj1size = obj1.size[index]
        obj2pos = obj2.center[index]
        obj2size = obj2.size[index]
        if obj1pos > obj2pos:
            if obj1pos - int(obj1size/2) <= obj2pos + int(obj2size/2):
                return True
        else:
            if obj1pos + int(obj1size/2) >= obj2pos - int(obj2size/2):
                return True
        return False

    def generateRaceImage(self):
        image = [[None for y in range(self.sizey)] for x in range(self.sizex)]

        for obj in [self.car] + self.obstacles:
            lower_left = obj.lowerLeft()
            for x in range(obj.size[0]):
                for y in range(obj.size[1]):
                    for z in range(obj.size[2]):
                        if obj.obj_matrix[x][y][z] == None:
                            continue
                        plain_point = self.inScope(lower_left[0]+x,lower_left[1]+y,lower_left[2]+z)
                        if plain_point == None:
                            continue
                        if image[plain_point[0]][plain_point[1]] == None:
                            image[plain_point[0]][plain_point[1]] = obj.obj_matrix[x][y][z]

        for x in range(self.sizex):
            for y in range(self.sizey):
                if image[x][y] == None:
                    if self.plain_offset[1] + y > 0:
                        image[x][y] = 1
                    else:
                        image[x][y] = 0

        return image

    def inScope(self, x, y, z):
        vector = fliputils.subVector((x,y,z), self.camera)
        vector = fliputils.normVector(vector)

        try:
            factor = (self.sizez - self.camera[2]) / vector[2]
        except ZeroDivisionError:
            return None

        endvector = fliputils.addVector(self.camera, fliputils.multiplyVector(vector, factor))

        if self.plain_offset[0] <= endvector[0] and self.plain_offset[0] + self.sizex > endvector[0] + 1 and self.plain_offset[1] <= endvector[1] and self.plain_offset[1] + self.sizey > endvector[1] + 1:
            return (int(round(endvector[0]-self.plain_offset[0])),int(round(endvector[1]-self.plain_offset[1])))

        return None

def pygameInputHandler(race):
    pygame.init()
    screen = pygame.display.set_mode((10,10))
    pygame.display.set_caption("FlipRace")
    pygame.mouse.set_visible(0)
    pygame.key.set_repeat(50,50)

    while not race.lost:
        c = ""
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_LEFT:
                    c = "l"
                elif event.key == K_RIGHT:
                    c = "r"
                elif event.key == K_p:
                    c = "p"
        if c:
            if c == "l":
                race.moveLeft()
            elif c == "r":
                race.moveRight()
            elif c == "p":
                race.togglePause()
        sleep(.05)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Race for Flipdot')
    parser.add_argument('--console-out', '-c', action='store_true', help='Print race on command line on each update')
    parser.add_argument('--invert', '-i', action='store_true', help='Invert the matrix values')
    parser.add_argument('--sizex', type=int, default=144, help='Size on the x axis')
    parser.add_argument('--sizey', type=int, default=120, help='Size on the y axis')
    parser.add_argument('--speed', type=int, default=15, help='Speed of the racecar')
    parser.add_argument('flipdotpanels', nargs='*', help='List of ip46:port strings for the flipdotpanels')
    args = parser.parse_args()

    hostsAndPorts = []
    for ipPort in args.flipdotpanels:
        ipPort = ipPort.replace("[","").replace("]","").rsplit(':',1)
        ipPort = (ipPort[0],int(ipPort[1]))
        hostsAndPorts.append(ipPort)

    race = Race(args.sizex, args.sizey, args.speed, hostsAndPorts, args.console_out, args.invert)
    race.start()
    try:
        pygameInputHandler(race)
    except KeyboardInterrupt:
        race.stop = True
