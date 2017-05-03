#!/usr/bin/env python3
from FlipdotAPI.FlipdotMatrix import FlipdotMatrix, FlipdotImage
from random import randint
from queue import Queue
from time import time, sleep
import threading
import argparse
import numpy as np
import socket
import fliputils

def overlaps(range1, range2):
    sort = lambda x: (x[0], x[1]) if x[0] < x[1] else (x[1], x[0])
    range1 = sort(range1)
    range2 = sort(range2)
    if range1[0] < range2[0] and range1[1] < range2[0]:
        return False
    if range1[0] > range2[1] and range1[1] > range2[1]:
        return False
    return True

class GraphicsObject:
    def __init__(self, size, pos):
        self.size = size
        self.center = pos

    def draw(self, matrix):
        lower_left = self.lower_left()
        for x in range(lower_left[0], lower_left[0]+self.size[0]):
            for y in range(lower_left[1], lower_left[1]+self.size[1]):
                matrix[x][y] = 1

    def lower_left(self):
        return (round(self.center[0]-(self.size[0]/2)), round(self.center[1]-(self.size[1]/2)))

    def upper_right(self):
        return (round(self.center[0]+(self.size[0]/2)), round(self.center[1]+(self.size[1]/2)))

class GameObject(GraphicsObject):
    def __init__(self, size, pos, speed = 1, direction=(0,0)):
        GraphicsObject.__init__(self, size, pos)
        self.speed = speed
        self.direction = direction
        self.prev_center = pos

    def move(self, boundaries):
        nv = fliputils.normVector(self.direction)
        self.prev_center = self.center
        self.center = fliputils.addVector(self.center, fliputils.multiplyVector(nv, self.speed))

        lower_left = self.lower_left()
        if lower_left[0] < 0:
            self.center = fliputils.addVector(self.center, fliputils.multiplyVector((1,0),abs(lower_left[0])))
        if lower_left[1] < 0:
            self.center = fliputils.addVector(self.center, fliputils.multiplyVector((0,1),abs(lower_left[1])))

        upper_right = self.upper_right()
        if upper_right[0] > boundaries[0]:
            self.center = fliputils.addVector(self.center, fliputils.multiplyVector((-1,0),upper_right[0]-boundaries[0]))
        if upper_right[1] > boundaries[1]:
            self.center = fliputils.addVector(self.center, fliputils.multiplyVector((0,-1),upper_right[1]-boundaries[1]))

        self.direction = nv

    def up(self):
        self.change_direction((0,1))

    def down(self):
        self.change_direction((0,-1))

    def stop(self):
        self.change_direction((0,0))

    def change_direction(self, direction):
        self.direction = direction

    def mirror_direction_x(self):
        self.direction = (-self.direction[0], self.direction[1])

    def mirror_direction_y(self):
        self.direction = (self.direction[0], -self.direction[1])

    def get_boundaries(self):
        return (self.lower_left(), self.upper_right())

class Player(GameObject):
    def __init__(self, size, pos, speed = 3, direction=(0,0), total_score = 0):
        GameObject.__init__(self, size, pos, speed, direction)
        self.score = 0
        self.total_score = total_score
        self.active = False

    def score_up(self):
        self.score += 1
        self.total_score += 1

    def ready(self):
        self.active = True

    def reset(self, center, new_game = False):
        self.center = center
        if new_game:
            self.active = False
            self.score = 0

class Ball(GameObject):
    def __init__(self, size, pos, speed = 6, direction=(0,0)):
        GameObject.__init__(self, size, pos, speed, direction)

    def bounce(self, players, boundaries):
        lower_left = self.lower_left()
        upper_right = self.upper_right()

        if lower_left[1] <= 0 or upper_right[1] >= boundaries[1]:
            self.mirror_direction_y()

        player_boundaries = players[0].get_boundaries()
        if self.direction[0] < 0 and overlaps((self.prev_center[0], self.center[0]-1), (player_boundaries[0][0], player_boundaries[1][0])) and overlaps((lower_left[1], upper_right[1]),(player_boundaries[0][1], player_boundaries[1][1])):
            self.mirror_direction_x()
            if players[0].direction == (0,1):
                self.change_direction(fliputils.addVector(self.direction, (1,1)))
            elif players[0].direction == (0,-1):
                self.change_direction(fliputils.addVector(self.direction, (1,-1)))

        player_boundaries = players[1].get_boundaries()
        if self.direction[0] > 0 and overlaps((self.prev_center[0], self.center[0]+1), (player_boundaries[0][0], player_boundaries[1][0])) and overlaps((lower_left[1], upper_right[1]),(player_boundaries[0][1], player_boundaries[1][1])):
            self.mirror_direction_x()
            if players[1].direction == (0,1):
                self.change_direction(fliputils.addVector(self.direction, (-1,1)))
            elif players[1].direction == (0,-1):
                self.change_direction(fliputils.addVector(self.direction, (-1,-1)))

class PlayerInputHandler(threading.Thread):
    def __init__(self, player, queue):
        threading.Thread.__init__(self, daemon = True)
        self.player = player
        self.queue = queue

    def run(self):
        while True:
            action = self.queue.get()
            if action == "UP":
                self.player.up()
            elif action == "DOWN":
                self.player.down()
            elif action == "LEFT":
                self.player.ready()
            elif action == "NONE":
                self.player.stop()

class InputHandler(threading.Thread):
    def __init__(self, players):
        threading.Thread.__init__(self, daemon = True)
        self.socket = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        self.address = ("", 5555)
        self.socket.bind(self.address)
        queues = (Queue(), Queue())
        self.playerInputHandlers = (
            (PlayerInputHandler(players[0],queues[0]), queues[0]),
            (PlayerInputHandler(players[1],queues[1]), queues[1])
        )
        self.playerIds = [None, None]
        for inputHandler in self.playerInputHandlers:
            inputHandler[0].start()
        self.start()

    def run(self):
        while True:
            msg = self.socket.recvfrom(1024)
            msg = msg[0].decode("utf-8")
            player_id, command = msg.split(" ")
            try:
                player = self.playerIds.index(player_id)
            except ValueError:
                for x in range(2):
                    if not self.playerIds[x]:
                        self.playerIds[x] = player_id
                        player = x
                if player not in self.playerIds:
                    ri = randint(0,1)
                    self.playerIds[ri] = player_id
                    player = ri
            self.playerInputHandlers[player][1].put(command)

class GameHandler:
    def __init__(self, size, speed, udpHostsAndPorts = [], console_out = False, invert = False, panel_defaults = False, ball_speed = 6, player_speed = 3):
        self.size = size
        self.speed = speed
        bar_size = (round(self.size[0]/18),round(self.size[1]/5))
        ball_size = (round(self.size[0]/18),round(self.size[0]/18))
        total_scores = self.loadScores()
        self.players = (
            Player(bar_size, (round(self.size[0]/18),round(self.size[1]/2)), speed = player_speed, total_score = total_scores[0]),
            Player(bar_size, (self.size[0] - round(self.size[0]/18),round(self.size[1]/2)), speed = player_speed, total_score = total_scores[1])
        )
        self.inputHandler = InputHandler(self.players)
        self.ball = Ball(ball_size, self.get_center(), speed = ball_speed)
        self.stop = False

        self.flipmatrix = FlipdotMatrix(imageSize = size) if panel_defaults else (FlipdotMatrix(udpHostsAndPorts, size) if len(udpHostsAndPorts) != 0 else None)
        self.flipdot_out = True if self.flipmatrix else False
        self.console_out = console_out
        self.invert = invert

    def loop(self):
        playing = False
        while not self.stop:
            t = time()
            new_game = self.step()
            if new_game:
                playing = False
                self.ball.stop()
            image = self.generatePongImage()
            if not playing:
                playing = all([x.active for x in self.players])
                if playing:
                    self.ball.change_direction((1,0))
            if self.invert:
                pass
            if self.flipdot_out:
                flipImage = FlipdotImage(np.flipud(image.T))
                score_string = "%d - %d" % (self.players[0].score, self.players[1].score)
                flipImage.blitTextAtPosition(score_string, xPos=self.get_center()[0]-2*(len(score_string)-1), yPos = 2*round(self.size[1]/12))
                total_score_string = "%d - %d" % (self.players[0].total_score, self.players[1].total_score)
                flipImage.blitTextAtPosition(total_score_string, xPos=self.get_center()[0]-2*(len(total_score_string)-1), yPos = (round(self.size[1]/12)))
                if not playing:
                    if not self.players[0].active:
                        flipImage.blitTextAtPosition("Press Left", xPos=self.players[0].upper_right()[0] + 2, yPos = self.size[1] - self.players[0].upper_right()[1])
                    if not self.players[1].active:
                        flipImage.blitTextAtPosition("Press Left", xPos=self.players[1].lower_left()[0] - 46, yPos = self.size[1] - self.players[1].upper_right()[1])
                self.flipmatrix.showImage(flipImage)
            if self.console_out:
                self.printImage(image)
            wait = (1./self.speed) - (time() - t)
            if wait > 0:
                sleep(wait)

    def printImage(self, image):
        for y in range(len(image[0])-1, -1, -1):
            line = ""
            for x in range(len(image)):
                line += "." if image[x][y] else " "
            print(line)

    def get_center(self):
        return (round(self.size[0]/2), round(self.size[1]/2))

    def generatePongImage(self):
        image = np.zeros(self.size,dtype=np.byte)

        for player in self.players:
            player.draw(image)
        self.ball.draw(image)

        return image

    def step(self):
        for player in self.players:
            player.move(self.size)
        self.ball.move(self.size)
        self.ball.bounce(self.players, self.size)
        ball_state = self.checkBallExit()
        if ball_state:
            self.ball.center = self.get_center()
            if ball_state == 1:
                self.ball.change_direction((-1,0))
                self.players[1].score_up()
            else:
                self.ball.change_direction((1,0))
                self.players[0].score_up()
            new_game = False
            if self.players[0].score == 5 or self.players[1].score == 5:
                new_game = True
            self.players[0].reset((round(self.size[0]/18), self.get_center()[1]), new_game)
            self.players[1].reset((self.size[0] - round(self.size[0]/18), self.get_center()[1]), new_game)
            self.saveScores()
            return new_game

    def saveScores(self):
        with open("scores", "w") as f:
            f.write("%d %d" % (self.players[0].total_score, self.players[1].total_score))

    def loadScores(self):
        try:
            with open("scores", "r") as f:
                lines = f.readlines()
            scores = [int(x) for x in lines[0].split(" ")]
        except:
            scores = (0,0)
        return scores

    def checkBallExit(self):
        return (1 if self.ball.lower_left()[0] <= 0 else (2 if self.ball.upper_right()[0] >= self.size[0] else 0))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Pong for Flipdot')
    parser.add_argument('--console-out', '-c', action='store_true', help='Print pong on command line on each update')
    parser.add_argument('--panel-defaults', '-d', action='store_true', help='Update flipdot panels but use API default hosts')
    parser.add_argument('--invert', '-i', action='store_true', help='Invert the matrix values')
    parser.add_argument('--sizex', type=int, default=144, help='Size on the x axis')
    parser.add_argument('--sizey', type=int, default=120, help='Size on the y axis')
    parser.add_argument('--speed', type=int, default=15, help='Speed of the game')
    parser.add_argument('--ball-speed', type=int, default=6, help='Speed of the game')
    parser.add_argument('--player-speed', type=int, default=3, help='Speed of the game')
    parser.add_argument('flipdotpanels', nargs='*', help='List of ip46:port strings for the flipdotpanels')
    args = parser.parse_args()

    hostsAndPorts = []
    for ipPort in args.flipdotpanels:
        ipPort = ipPort.replace("[","").replace("]","").rsplit(':',1)
        ipPort = (ipPort[0], int(ipPort[1]))
        hostsAndPorts.append(ipPort)

    game = GameHandler((args.sizex, args.sizey), args.speed, hostsAndPorts, args.console_out, args.invert, args.panel_defaults, args.ball_speed, args.player_speed)
    game.loop()
