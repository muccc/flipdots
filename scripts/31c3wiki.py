from FlipdotAPI.FlipdotMatrix import FlipdotMatrix
import sys
import os
import string
import time

def getHtml():
    html = os.popen("wget --no-check-certificate -qO- https://muc.pads.ccc.de/ep/pad/export/flipdot/latest?format=txt").readlines()
    return string.join(html)

def run():
    old_html = ""
    while True:
        time.sleep(2.0)
        old_html = run_once(old_html)

def run_once(old_html = ""):
    html = getHtml()[0:2000]
    if (html != old_html):
        matrix = FlipdotMatrix()
        matrix.showText(html)
#        print html
    return html

#main
if (__name__=="__main__"):
    run()

