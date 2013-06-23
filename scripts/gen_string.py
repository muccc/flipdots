import socket, time
import Image, ImageFont, ImageDraw, sys
import fileinput

UDPHOST="2001:7f0:3003:cafe:222:f9ff:fe01:c65"
UDPPORT=2323

FPS = 3

IMG_SIZE = (40, 16)
FONT_SIZE = 8
FONT_OFFSET= (1, -1)

C_BLACK = (0, 0, 0)
C_WHITE = (255, 255, 255)

sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)

def list2byte(l):
    byte = 0
    i = 0
    for i in range(8):
        byte += 2**(7-i) if l[i] else 0
    return byte

def array2packet(a):
    return str(bytearray([list2byte(a[i*8:i*8+8]) for i in range(len(a)/8)]))

def str2array(s):
    image = Image.new("RGBA", IMG_SIZE, C_BLACK)
    draw = ImageDraw.Draw(image)
    draw.fontmode = "1"         # No AA
    font = ImageFont.load_default()
    # font = ImageFont.truetype("FreeSans.ttf", FONT_SIZE)

    draw.text(FONT_OFFSET, s, font=font, fill=C_WHITE)

    imgmap = []
    for pixel in image.getdata():
        r, g, b, a = pixel
        if r == 255:
            imgmap.append(1)
        else:
            imgmap.append(0)
    return imgmap

while True:
    text = sys.stdin.readline()
    if text == "":
        break
    sock.sendto(array2packet(str2array(text.strip())), (UDPHOST, UDPPORT))
    time.sleep(1.0/FPS)
