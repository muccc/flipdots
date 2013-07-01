#!/usr/bin/python
import httplib, time
from FlipdotAPI.FlipdotMatrix import FlipdotMatrix

class HqStatusFlipdotAdapter(object):
    def __init__(self, 
                 flipdotMatrix = FlipdotMatrix(), 
                 uberbusHostAndPort=("uberbus.club.muc.ccc.de", 8080)
                 ):
        self.__flipdotMatrix = flipdotMatrix
        self.__uberbusHostAndPort = uberbusHostAndPort
        self.__oldHqStatus = "" 

    def runOnce(self):
        hqstatus = self.getHqStatusFromUberbus()
        self.showStatusTextWithoutBeginningHq(hqstatus)
        
    def showStatusTextWithoutBeginningHq(self, hqstatus):
        hqstatus = hqstatus[3:]
        self.showStatusText(hqstatus)   
        
    def showStatusText(self, hqstatus):
        self.__flipdotMatrix.showBlitText(hqstatus)
        
    def run(self):
        while True:
            newHqStatus = self.getHqStatusFromUberbus()
            if (newHqStatus != self.__oldHqStatus): 
                self.showStatusTextWithoutBeginningHq(newHqStatus)
                self.__oldHqStatus = newHqStatus
            time.sleep(5.0)
        
    def getHqStatusFromUberbus(self):
        try:
            conn = httplib.HTTPConnection(self.__uberbusHostAndPort[0]+":"+str(self.__uberbusHostAndPort[1]))
            conn.request("GET", "/")
            r1 = conn.getresponse()
            if (r1.status == 200):
                return r1.read()
            else:
                return "hq unknown"
        except:
            return "hq fnord"

#main
if (__name__=="__main__"):
    HqStatusFlipdotAdapter().run()
