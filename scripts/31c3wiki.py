from FlipdotAPI.FlipdotMatrix import FlipdotMatrix
import sys
import os
import string
import time

def getHtml():
    html = os.popen("wget --no-check-certificate -qO- https://muc.pads.ccc.de/ep/pad/export/flipdot/latest?format=txt").readlines()
    return string.join(html)

#main
if (__name__=="__main__"):
    while True:
        html = getHtml()
        matrix = FlipdotMatrix()
        matrix.showText(html)
        time.sleep(5.0)
        


