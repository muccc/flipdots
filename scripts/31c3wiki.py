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
    html = getHtml()[0:1000]
    if (html != old_html):
        matrix = FlipdotMatrix()
#        html =  "wiki.muc.ccc.de/flipdot:32c3\n"+html
        matrix.showText("wiki.muc.ccc.de/flipdot:33c3\n"+html)
    return html

#main
if (__name__=="__main__"):
    sys.setrecursionlimit(2028)
    run()

