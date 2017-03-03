#!/usr/bin/env python3
import base64
from io import BytesIO
from flask import Flask
from flask import redirect, render_template, request

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
    return "<html><head><title>FlipdotDebugPage</title></head><body <body style='font-size:6vh; line-height:2em;'><h3>"+msg+"</h3><ul><li><a href='/reset'>reset all</a></li><li><a href='/white'>white</a></li><li><a href='/black'>black</a></li><li><a href='/chess'>chess</a></li><li><a href='/static/flipdot-web-editor/index.html'>Image App</a></li></ul></body></html>"

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

@app.route("/png", methods=['POST'])
def png():
    from PIL import Image
    if request.method == 'POST':
        png = request.form['png']
        png = png.split(",",1)[1]
        im = Image.open(BytesIO(base64.b64decode(png)))
        im.rotate(90)
        imageArray = [[0 for x in range(wandwidth)] for y in range(wandheight)]
        for y in range(wandheight):
            for x in range(wandwidth):
                imageArray[y][x] = 1 if im.getpixel((x,y))[0] == 255 else 0
        image = FlipdotImage(imageArray)
        matrix.show(image)
        return ""
    else:
        return redirect("/")

if __name__ == "__main__":
    app.run(host='::', port=80)
