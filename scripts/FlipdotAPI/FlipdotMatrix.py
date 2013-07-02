import socket
from font import font8px

class FlipdotMatrix():
    def __init__(self, 
                 udpHostAndPort = ("2001:7f0:3003:cafe:222:f9ff:fe01:c65",2323), 
                 imageSize=(40, 16)
                 ):
        self.__sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        self.udpHostAndPort=udpHostAndPort
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
    
    def __showSerializedArrayOfPixels(self, imageArray):
        udpPacket = FlipdotMatrix.__arrayToPacket(imageArray) 
        self.__sendUdpPackage(udpPacket)

    def show(self, image):
        """
        send FlipdotImage to display. fills up with black pixels
        """
        self.__clearFlipdotImageWithoutUpdate()
        self.flipdotImage.blitImageAtPosition(image)
        self.__updateFlipdotMatrix()

    def showBlit (self, image, xPos=0, yPos=0):
        """
        send FlipdotImage to display, keeps old pixels around
        """ 
        self.flipdotImage.blitImageAtPosition(image, xPos, yPos)
        self.__updateFlipdotMatrix()

    def __updateFlipdotMatrix(self):
        serializedImageArray = self.flipdotImage.serializeImageArray()
        self.__showSerializedArrayOfPixels(serializedImageArray)
    
    def clear(self):
        """
        clears display. fills with black pixels
        """
        self.__clearFlipdotImageWithoutUpdate()
        self.__updateFlipdotMatrix()
    
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
        self.__updateFlipdotMatrix()

    def showBlitText(self, text, linebreak=False, xPos=0, yPos=0):
        """
        print text to display, keeps old pixels around
        """
        self.flipdotImage.blitTextAtPosition(text, linebreak, xPos, yPos)
        self.__updateFlipdotMatrix()

    @staticmethod
    def __arrayToPacket(imageArray):
        return str(bytearray([FlipdotMatrix.__list2byte(imageArray[i*8:i*8+8]) for i in range(len(imageArray)/8)]))
    
    @staticmethod
    def __list2byte(ArrayOfBinaryInts):
        byte  = 0
        for i in range(8):
            byte += 2**(7-i) if ArrayOfBinaryInts[i] else 0
        return byte

    
    def __sendUdpPackage(self, udpPacket):
        self.__sock.sendto(udpPacket, self.udpHostAndPort)
        


class FlipdotImage(object):
    BLACKPIXEL = 0
    WHITEPIXEL = 1

    def __init__(self, pixel2DArray):
        self.width = len(pixel2DArray[0])
        self.height = len(pixel2DArray)
        self.rowArrayOfLineArraysOfPixels =  pixel2DArray

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

    def blitTextAtPosition(self, text, autoLineBreak = False, xPos = 0, yPos = 0, __indentXPos=None):
        if __indentXPos==None:
            __indentXPos = xPos

        if len(text) <= 0:
            return
        
        letterImage = self.__getLetterImageForNextLetter(text)
        
        if self.__isLineBreakRequired(text, autoLineBreak, letterImage, xPos):
            xPos = __indentXPos
            yPos = yPos + font8px["lineheight"]
            
        self.blitImageAtPosition(letterImage, xPos, yPos)
        
        nextLetterXPos = xPos + letterImage.width + font8px["whitespace"]
        self.blitTextAtPosition(text[1:], autoLineBreak, nextLetterXPos, yPos, __indentXPos)
    
    def __isLineBreakRequired(self, text, autoLineBreak, letterImage, xPos):
        if text[:1] == "\n":
            return True
        elif autoLineBreak and self.__isEndOfLineReached(letterImage, xPos):
            return True
        else:
            return False
                
    def __isEndOfLineReached(self, letterImage, xPos):
        return letterImage.width > self.width-xPos

    def __getLetterImageForNextLetter(self, text):
        nextLetter = text[:1].upper()
        if not nextLetter in font8px:
            nextLetter="?"
        return FlipdotImage(font8px[nextLetter])

    def serializeImageArray(self):
        imageArray = []
        for y in range(self.height):
            for x in range(self.width):
                imageArray.append(self.rowArrayOfLineArraysOfPixels[y][x])
        return imageArray

    def getLine(self, line):
        return self.rowArrayOfLineArraysOfPixels[line]
        
    @classmethod
    def newBlackFlipdotImage(cls, width, height):
        pixel2DArray = cls.generateColoredRowArrayOfLineArraysOfPixels(width, height, FlipdotImage.BLACKPIXEL) 
        return cls(pixel2DArray)

    @classmethod
    def newWhiteFlipdotImage(cls, width, height):
        pixel2DArray = cls.generateColoredRowArrayOfLineArraysOfPixels(width, height, FlipdotImage.WHITEPIXEL) 
        return cls(pixel2DArray)
    
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

#main
if (__name__=="__main__"):
    matrix = FlipdotMatrix()
    matrix.resetAll()
    matrix.showText("flip the dots!", True)    
    
    
