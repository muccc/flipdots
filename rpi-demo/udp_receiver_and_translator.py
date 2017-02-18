import thread
import socket
import pygame
from pygame.locals import *
from os import system
from time import sleep
from threading import Thread


class PowerManager(Thread):
    def __init__(self, timeouttime=60):
        Thread.__init__(self)
        self.running = False
        self.state = False
        self.timer = 0
        self.timeouttime = timeouttime
        self.start()
       
    def run(self):
        self.running = True
        
        while self.running:
            if (self.isAlreadyTimedOut() and self.isPowered()):
                self.disablePower()
            elif (self.shouldBePowered() and self.isNotPowered()):
                self.enablePower()
            self.timer+=1
            sleep(1)

        

    def stopThisThread(self):
        self.running = False
        self.disablePower()

    def isAlreadyTimedOut(self):
        return self.timer > self.timeouttime 

    def isPowered(self):
        return self.state

    def isNotPowered(self):
        return not self.isPowered()

    def shouldBePowered(self):
        return not self.isAlreadyTimedOut()

    def enablePower(self):
        self.setPower(1)
        self.state = True
        
    def disablePower(self):
        self.setPower(0)
        self.state = False

    def setPower(self, value):
        system("/bin/echo '%d' > /sys/class/gpio/gpio17/value" % value)

    def notify(self):
        self.timer = 0
        self.sleepIfIsNotPowered()

    def sleepIfIsNotPowered(self):
        if self.isNotPowered():
            sleep(3)

    

                

class matrixMapping():
    def __init__(self, 
                 udpPort = 2323):
        self.udpPort = udpPort
        self.outputport = 2342
        self.udpHostSocket = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        self.udpHostSocket.bind(("", self.udpPort))
        self.udpHostSocket4 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpHostSocket4.bind(("", self.udpPort+1))
        self.outputSocket = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        self.PowerThread = PowerManager()


    def run(self):
	thread.start_new_thread ( self.RunServer, () )
	thread.start_new_thread ( self.RunServer4, () )
	#self.RunServer()

    def RunServer(self):
        try: 
            while True:
                rawData = self.udpHostSocket.recv(4096)
                imageArray = ImageArrayAdapter().convertPacketToImageArray(rawData)
                self.translateAndSend(imageArray)
        finally: 
            self.udpHostSocket.close()
            self.PowerThread.stopThisThread()

    def RunServer4(self):
        try: 
            while True:
                rawData = self.udpHostSocket4.recv(4096)
                imageArray = ImageArrayAdapter().convertPacketToImageArray(rawData)
                self.translateAndSend(imageArray)
        finally: 
            self.udpHostSocket.close()
            self.PowerThread.stopThisThread()

    def translateAndSend(self, imageArray):
        imageArray = self.doZeile2DMapping(imageArray)
        packet =  str(bytearray([matrixMapping.__list2byte(imageArray[i*8:i*8+8]) for i in range(len(imageArray)/8)]))
    
        self.PowerThread.notify()
        self.outputSocket.sendto(packet, ("localhost",2342))

        

    @staticmethod
    def __list2byte(ArrayOfBinaryInts):
        byte  = 0
        for i in range(8):
            byte += 2**(7-i) if ArrayOfBinaryInts[i] else 0
        return byte

    def doZeile2DMapping(self, linearInput):
        ## spilt to several panel-matrixes
        panels = []
        for i in range(11):
            panels.append([])
            for y in range(20):
                panels[i].append([])
        
        for y in range (20):
            for i in range(11):
                for x in range(16):
                    if len(linearInput) > 0:
                         panels[i][y].append(linearInput.pop(0))
                    else:
                         panels[i][y].append(0)

                panels[i][y].reverse()


        ## transpose panels
        for i in range(11):
            panels[i] = zip(*panels[i])

        
        ## bring panels to right order:
        rightpanels = []
        for i in range(6):
            rightpanels.append(panels[10-i])

        leftpanels = []
        for i in range(5):
            leftpanels.append(panels[4-i])

        ## add blank panel for fnord!
        blankpanel=[]
        for y in range(16):
            blankpanel.append([])
            for x in range(20):
                blankpanel[y].append(0)

        leftpanels.append(blankpanel)
        
        ## linearize output
        linearOutput = []
            
        for y in range(16):
            for i in range(6):
                for x in range(20):
                    linearOutput.append(rightpanels[i][y][x])

        for y in range(16):
            for i in range(6):
                for x in range(20):
                    linearOutput.append(leftpanels[i][y][x])

            

        return linearOutput



class ImageArrayAdapter():
    def __init__(self):
        self.arrayOfBinaryInts = []

    def convertPacketToImageArray(self, udpPacketStr):
        self.arrayOfBinaryInts = []
        byteArray = bytearray(udpPacketStr)
        for byte in byteArray:
            self.__appendByteToArrayOfBinaryInts(byte)
        return self.arrayOfBinaryInts
    
    def __appendByteToArrayOfBinaryInts(self, byte):
        byteValue = int(byte)
        for i in range(8):
            if byteValue/(2**(7-i)) > 0:
                self.arrayOfBinaryInts.append(1)
            else: 
                self.arrayOfBinaryInts.append(0)
            byteValue = byteValue%(2**(7-i))


     
if __name__ == '__main__':
    matrixMapping(udpPort=2323).run()
        



