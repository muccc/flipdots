#!/usr/bin/env python2
from FlipdotAPI.FlipdotMatrix import FlipdotMatrix, FlipdotImage
from time import sleep
import datetime
import math

class Clock:
    def __init__(self, sizex = 144, sizey = 120, radius = 50, udpHostsAndPorts = []):
        self.matrix = FlipdotMatrix(udpHostsAndPorts, (sizex, sizey))
        self.sizex = sizex
        self.sizey = sizey
        self.radius = radius
        self.center = (int(self.sizex/2), int(self.sizey/2))

    def loop(self):
        try:
            while True:
                flipImage = FlipdotImage(self.generateClockImage())
                self.matrix.show(flipImage)
                sleep(1)
        except KeyboardInterrupt:
            return

    def generateClockImage(self):
        image = [[0 for y in range(self.sizey)] for x in range(self.sizex)]
        time = datetime.datetime.now().time()

        image[self.center[0]][self.center[1]] = 1
        hour_coords = self.circlePoint(- math.radians((((time.hour%12)/12.) if time.hour else 0)*360 + 180 + (time.minute/2)))
        minute_coords = self.circlePoint(- math.radians(time.minute*6+180))
        second_coords = self.circlePoint(- math.radians(time.second*6+180))

        for i in range(60):
            degree = i*6 + 90
            radian = - math.radians(degree)
            coords = self.circlePoint(radian)

            if not i % 5:
                self.addLine(image, coords, self.center, 3, 1)
            else:
                self.addLine(image, coords, self.center, 1)

        self.addLine(image, self.center, hour_coords, int(self.radius / 3), 1)
        self.addLine(image, self.center, minute_coords, int(self.radius / 2))
        self.addLine(image, self.center, second_coords, self.radius - 3)

        for x in range(self.radius*2):
            line = ""
            for y in range(self.radius*2):
                line = line + ("." if image[(self.center[0]-self.radius)+x][(self.center[1]-self.radius)+y] else " ")
            print line

        return image

    def circlePoint(self, t):
        return (int(round(self.radius*math.cos(t))) + self.center[0], int(round(self.radius*math.sin(t))) + self.center[1])

    def addLine(self, image, source, destination, length, thickness = 0):
        vector = self.subVector(destination, source)
        vector = self.normVector(vector)
        perp_vector = (-vector[1], vector[0])

        for i in range(1,length+1):
            coords = self.addVector(source, self.multiplyVector(vector, i))
            image[int(round(coords[0]))][int(round(coords[1]))] = 1
            if thickness > 0:
                perp_start = self.addVector(coords, self.multiplyVector(perp_vector, thickness))
                for j in range(0, thickness*2+1):
                    perp_coords = self.addVector(perp_start, self.multiplyVector(perp_vector, -j))
                    image[int(round(perp_coords[0]))][int(round(perp_coords[1]))] = 1

    def normVector(self, v):
        length = math.sqrt(sum([i**2 for i in v]))
        new_v = []
        for i in range(len(v)):
            new_v.append(v[i]/length)
        return tuple(new_v)

    def subVector(self, v1, v2):
        res = []
        for i in range(len(v1)):
            res.append(v1[i]-v2[i])
        return tuple(res)

    def addVector(self, v1, v2):
        res = []
        for i in range(len(v1)):
            res.append(v1[i]+v2[i])
        return tuple(res)

    def multiplyVector(self, v, multiplier):
        return tuple([i*multiplier for i in v])

if __name__=='__main__':
    clock = Clock(udpHostsAndPorts = [("2001:7f0:3003:235e:ba27:ebff:feb9:db12", 2323),
                                    ("2001:7f0:3003:235e:ba27:ebff:fe23:60d7", 2323),
                                    ("2001:7f0:3003:235e:ba27:ebff:fe71:dd32", 2323)])
    clock.loop()
