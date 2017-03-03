#!/usr/bin/env python
from flask import Flask
from flask import render_template

from FlipdotAPI.FlipdotMatrix import FlipdotMatrix, FlipdotImage


wandwidth = 144
wandheight = 120

app = Flask(__name__)
matrix = FlipdotMatrix(
    udpHostsAndPorts = [
        ("fe80::ba27:ebff:feb9:db12",2323),
        ("fe80::ba27:ebff:fe23:60d7", 2323),
        ("fe80::ba27:ebff:fe71:dd32", 2323)
        ],
    imageSize=(wandwidth, wandheight),
    transposed = True
    )


def minipage(msg):
    return "<html><head><title>FlipdotDebugPage</title></head><body <body style='font-size:6vh; line-height:2em;'><h3>"+msg+"</h3><ul><li><a href='/reset'>reset all</a></li><li><a href='/white'>white</a></li><li><a href='/black'>black</a></li><li><a href='/chess'>chess</a></li></ul></body></html>"

@app.route("/")
def hello():
    return minipage("")

@app.route("/reset")
def reset():
    matrix.resetAll()
    return minipage("reseted all")

@app.route("/black")
def black():
    blackImage = FlipdotImage.newBlackFlipdotImage(wandwidth, wandheight)
    matrix.show(blackImage)
    return minipage("blacked all")

@app.route("/white")
def white():
    whiteImage = FlipdotImage.newWhiteFlipdotImage(wandwidth, wandheight)
    matrix.show(whiteImage)
    return minipage("whited all!")

@app.route("/chess")
def chess():
    imageArray = [[0 for x in range(wandwidth)] for y in range(wandheight)]
    for y in range(wandheight):
        for x in range(wandwidth):
            imageArray[y][x] = (x+y)%2

    image = FlipdotImage(imageArray)
    matrix.show(image)
    return minipage("chess!")




if __name__ == "__main__":
    app.run(host='::', port=80)
