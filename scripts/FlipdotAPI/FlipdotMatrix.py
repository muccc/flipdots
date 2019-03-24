#!/usr/bin/env python3
import socket
import numpy as np
try:
    from FlipdotAPI import config
    from FlipdotAPI.font import font8px
except ImportError:
    import config
    from font import font8px

class FlipdotMatrix():
    def __init__(self,


                 udpHostsAndPorts = config.panelAddressArray,
                 imageSize=(144, 120),
                 transposed = config.transposed
                 ):
        self.__sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        self.transposed = transposed
        self.udpHostsAndPorts=udpHostsAndPorts
        self.numberOfMatrixes = len(udpHostsAndPorts)
        self.MatrixSize = (int(imageSize[0]/self.numberOfMatrixes), imageSize[1])
        self.flipdotImage = FlipdotImage.newBlackFlipdotImage(imageSize[0], imageSize[1])

    def resetAll(self):
        """
        flip every pixel at least once, end with cleared Matrix
        """
        width = self.flipdotImage.width
        height = self.flipdotImage.height
        whiteImage = FlipdotImage.newWhiteFlipdotImage(width, height)
        blackImage = FlipdotImage.newBlackFlipdotImage(width, height)
        self.show(whiteImage)
        self.show(blackImage)

    def __showSerializedArrayOfPixels(self, imageArray, udpHostAndPort):
        udpPacket = FlipdotMatrix.__arrayToPacket(imageArray)
        self.__sendUdpPackage(udpPacket, udpHostAndPort)

    def show(self, image):
        """
        send FlipdotImage to display. fills up with black pixels
        """
        self.__clearFlipdotImageWithoutUpdate()
        self.flipdotImage.blitImageAtPosition(image)
        self.__updateFlipdotMatrixes()

    def showImage(self, image):
        self.flipdotImage = image
        self.__updateFlipdotMatrixes()

    def showBlit (self, image, xPos=0, yPos=0):
        """
        send FlipdotImage to display, keeps old pixels around
        """
        self.flipdotImage.blitImageAtPosition(image, xPos, yPos)
        self.__updateFlipdotMatrixes()

    def __updateFlipdotMatrixes(self):
        cuts = np.hsplit(self.flipdotImage.rowArrayOfLineArraysOfPixels, self.numberOfMatrixes)
        for i in range(self.numberOfMatrixes):
            serializedImageArray = cuts[i].ravel() if not self.transposed else cuts[i].T.ravel()
            udpHostAndPort = self.udpHostsAndPorts[i]
            self.__showSerializedArrayOfPixels(serializedImageArray, udpHostAndPort)

    def clear(self):
        """
        clears display. fills with black pixels
        """
        self.__clearFlipdotImageWithoutUpdate()
        self.__updateFlipdotMatrixes()

    def __clearFlipdotImageWithoutUpdate(self):
        width = self.flipdotImage.width
        height = self.flipdotImage.height
        self.flipdotImage = FlipdotImage.newBlackFlipdotImage(width, height)

    def showText(self, text, linebreak = False, xPos=0, yPos = 0):
        """
        print text to display
        """
        self.__clearFlipdotImageWithoutUpdate()
        self.flipdotImage.blitTextAtPosition(text, linebreak, xPos, yPos)
        self.__updateFlipdotMatrixes()

    def showBlitText(self, text, linebreak=False, xPos=0, yPos=0):
        """
        print text to display, keeps old pixels around
        """
        self.flipdotImage.blitTextAtPosition(text, linebreak, xPos, yPos)
        self.__updateFlipdotMatrixes()

    @staticmethod
    def __arrayToPacket(imageArray):
        return bytearray([FlipdotMatrix.__list2byte(imageArray[i*8:i*8+8]) for i in range(int(len(imageArray)/8))])

    @staticmethod
    def __list2byte(ArrayOfBinaryInts):
        byte  = 0
        for i in range(8):
            byte += 2**(7-i) if ArrayOfBinaryInts[i] else 0
        return byte

    def __sendUdpPackage(self, udpPacket, udpHostAndPort):
        self.__sock.sendto(udpPacket, udpHostAndPort)



class FlipdotImage(object):
    BLACKPIXEL = 0
    WHITEPIXEL = 1

    def __init__(self, pixel2DArray):
        self.width = len(pixel2DArray[0])
        self.height = len(pixel2DArray)
        self.rowArrayOfLineArraysOfPixels = np.array(pixel2DArray)

    def blitImageAtPosition(self, flipdotImage, xPos=0, yPos=0):
        for lineNr in range(self.height):
            newImageLineNr = lineNr-yPos
            if newImageLineNr >= 0 and flipdotImage.height > newImageLineNr:
                self.__blitLineAtPosition(flipdotImage, lineNr, newImageLineNr, xPos, yPos)

    def __blitLineAtPosition(self, flipdotImage, lineNr, newImageLineNr, xPos, yPos):
        for rowNr in range(self.width):
            newImageRowNr = rowNr - xPos
            if newImageRowNr >= 0 and flipdotImage.width > newImageRowNr:
                self.rowArrayOfLineArraysOfPixels[lineNr][rowNr] = flipdotImage.rowArrayOfLineArraysOfPixels[newImageLineNr][newImageRowNr]

    def blitTextAtPosition(self, text, autoLineBreak = False, xPos = 0, yPos = 0):
        indentXPos = xPos

        for char in text:
            letterImage = self.__getLetterImageForCharacter(char)

            if self.__isLineBreakRequired(char, autoLineBreak, letterImage, xPos):
                xPos = indentXPos
                yPos = yPos +font8px["lineheight"]

            self.blitImageAtPosition(letterImage, xPos, yPos)

            xPos = xPos + letterImage.width + font8px["whitespace"]

    def __isLineBreakRequired(self, char, autoLineBreak, letterImage, xPos):
        if char == "\n":
            return True
        elif autoLineBreak and self.__isEndOfLineReached(letterImage, xPos):
            return True
        else:
            return False

    def __isEndOfLineReached(self, letterImage, xPos):
        return letterImage.width > self.width-xPos

    def __getLetterImageForNextLetter(self, text):
        nextLetter = text[:1]
        return self.__getLetterImageForCharacter(nextLetter)

    def __getLetterImageForCharacter(self, char, uppercase = True):
        if uppercase:
            char = char.upper()
        if not char in font8px:
            char = "?"
        return FlipdotImage(font8px[char])

    def serializeImageArray(self, transposed = False):
        if transposed:
            return self.rowArrayOfLineArraysOfPixels.T.ravel()

        return self.rowArrayOfLineArraysOfPixels.ravel()

    def getLine(self, line):
        return self.rowArrayOfLineArraysOfPixels[line]

    def getSinglePixel(self, x, y):
        return self.rowArrayOfLineArraysOfPixels[y][x]


    @classmethod
    def newBlackFlipdotImage(cls, width, height):
        pixel2DArray = cls.generateColoredRowArrayOfLineArraysOfPixels(width, height, FlipdotImage.BLACKPIXEL)
        return cls(pixel2DArray)

    @classmethod
    def newWhiteFlipdotImage(cls, width, height):
        pixel2DArray = cls.generateColoredRowArrayOfLineArraysOfPixels(width, height, FlipdotImage.WHITEPIXEL)
        return cls(pixel2DArray)

    @classmethod
    def newPartOfAnotherFlipdotImage(cls, oldFlipdotImage, newSize, offset):
        pixel2DArray = cls.cutPartOfAnotherFlipdotImage(oldFlipdotImage, newSize, offset)
        return cls(pixel2DArray)

    @classmethod
    def cutPartOfAnotherFlipdotImage(cls, oldFlipdotImage, newSize, offset):
        width = newSize[0]
        height = newSize[1]
        xOffset = offset[0]
        yOffset = offset[1]
        rowArrayOfLineArrayOfPixels = []
        for y in range(height):
            lineArrayOfPixels = []
            for x in range(width):
                lineArrayOfPixels.append(oldFlipdotImage.getSinglePixel(xOffset+x, yOffset+y))
            rowArrayOfLineArrayOfPixels.append(lineArrayOfPixels)
        return rowArrayOfLineArrayOfPixels


    @staticmethod
    def generateColoredRowArrayOfLineArraysOfPixels(width, height, color):
        rowArrayOfLineArrayOfPixels = []
        for y in range(height):
            rowArrayOfLineArrayOfPixels.append(FlipdotImage.generateColoredLineArrayOfPixels(width, color))
        return rowArrayOfLineArrayOfPixels

    @staticmethod
    def generateColoredLineArrayOfPixels(width, color):
        lineArrayOfPixels = []
        for x in range(width):
            lineArrayOfPixels.append(color)
        return lineArrayOfPixels

    def __eq__(self, other):
        return (self.rowArrayOfLineArraysOfPixels == other.rowArrayOfLineArraysOfPixels).all()

#main
if (__name__=="__main__"):
    matrix = FlipdotMatrix()
    matrix.resetAll()
    matrix.showText("\n \n \n   Bitte gehen Sie weiter!\n \n \n Hier gibt es nichts zu sehen\n ", True)
#    matrix.showText(sys.argv[1])
