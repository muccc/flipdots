#!/usr/bin/env python2
from FlipdotAPI.FlipdotMatrix import FlipdotMatrix, FlipdotImage
from time import sleep
import argparse
import datetime
import math

class Clock:
    def __init__(self, sizex = 144, sizey = 120, radius = 50, udpHostsAndPorts = [],
            hour_hand = True, minute_hand = True, second_hand = True, console_out = False,
            run_once = False):
        self.matrix = FlipdotMatrix(udpHostsAndPorts, (sizex, sizey)) if len(udpHostsAndPorts) != 0 else None
        self.sizex = sizex
        self.sizey = sizey
        self.radius = radius
        self.center = (int(self.sizex/2), int(self.sizey/2))
        self.hour_hand = hour_hand
        self.minute_hand = minute_hand
        self.second_hand = second_hand
        self.console_out = console_out
        self.flipdot_out = len(udpHostsAndPorts) != 0
        self.run_once = run_once

    def loop(self):
        sleep_time = 1 if self.second_hand else 60
        try:
            while True:
                flipImage = FlipdotImage(self.generateClockImage())
                if self.flipdot_out:
                    self.matrix.show(flipImage)
                if self.run_once:
                    break
                sleep(sleep_time)
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

        if self.hour_hand:
            self.addLine(image, self.center, hour_coords, int(self.radius / 3), 1)
        if self.minute_hand:
            self.addLine(image, self.center, minute_coords, int(self.radius / 2))
        if self.second_hand:
            self.addLine(image, self.center, second_coords, self.radius - 3)

        if self.console_out:
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
    parser = argparse.ArgumentParser(description='Clock for Flipdot')
    parser.add_argument('--no-hour', '-H', action='store_true', help='Do not display hour hand')
    parser.add_argument('--no-minute', '-M', action='store_true', help='Do not display minute hand')
    parser.add_argument('--no-second', '-S', action='store_true', help='Do not display second hand')
    parser.add_argument('--console-out', '-c', action='store_true', help='Print clock on command line on each update')
    parser.add_argument('--run-once', '-r', action='store_true', help='Run only once, useful in combination with watch command')
    parser.add_argument('--sizex', type=int, default=144, help='Size on the x axis')
    parser.add_argument('--sizey', type=int, default=120, help='Size on the y axis')
    parser.add_argument('--radius', type=int, default=60, help='Radius of the clock')
    parser.add_argument('flipdotpanels', nargs='*', help='List of ip46:port strings for the flipdotpanels')
    args = parser.parse_args()

    hostsAndPorts = []
    for ipPort in args.flipdotpanels:
        ipPort = ipPort.replace("[","").replace("]","").rsplit(':',1)
        ipPort = (ipPort[0],int(ipPort[1]))
        hostsAndPorts.append(ipPort)

    clock = Clock(args.sizex,args.sizey,args.radius,
            udpHostsAndPorts = hostsAndPorts, hour_hand = not args.no_hour,
            minute_hand = not args.no_minute, second_hand = not args.no_second,
            console_out = args.console_out, run_once = args.run_once)
    clock.loop()
