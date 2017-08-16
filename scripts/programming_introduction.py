#!/usr/bin/env python3
#
# This is a Work-In-Progress attempt to create a template for introducing interested people in programming.
# The template provides a basic skeleton for quickly bringing content on the Flipdot panel while being able to explore basic programming techniques.

import argparse
from time import sleep
from FlipdotAPI.FlipdotMatrix import FlipdotMatrix, FlipdotImage

def main_loop(sizex, sizey, udpHostsAndPorts = [], console_out = False, api_defaults = False, update_interval = 0):
    if len(udpHostsAndPorts) != 0:
        flipdot_matrix = FlipdotMatrix(udpHostsAndPorts, (sizex, sizey))
        flipdot_out = True
    elif api_defaults:
        flipdot_matrix = FlipdotMatrix(imageSize=(sizex,sizey))
        flipdot_out = True
    else:
        flipdot_matrix = None
        flipdot_out = False

    pixel_matrix = generateEmptyMatrix(sizex, sizey)

    try:
        while True:
            pixel_matrix = step(pixel_matrix, sizex, sizey)
            if console_out:
                printToConsole(pixel_matrix, sizex, sizey)
            if flipdot_out:
                flipImage = FlipdotImage(prepareMatrixForAPI(pixel_matrix, sizex, sizey))
                matrix.show(flipImage, sizex, sizey)
            sleep(update_interval)
    except KeyboardInterrupt:
        return

def prepareMatrixForAPI(pixel_matrix, sizex, sizey):
    tmp_image = [[0 for x in range(sizex)] for y in range(sizey)]
    for x in range(sizex):
        for y in range(sizey):
            tmp_image[y][x] = pixel_matrix[x][sizey - y - 1]

    return tmp_image

def printToConsole(pixel_matrix, sizex, sizey):
    for y in range(sizey):
        line = ""
        for x in range(sizex):
            line = line + ("." if pixel_matrix[x][sizey-y-1] else " ")
        print(line)

def generateEmptyMatrix(sizex, sizey):
    return [[0 for y in range(sizey)] for x in range(sizex)]


def show(pixel_matrix, flipdot_matrix, flipdot_out, console_out, sizex, sizey):
    if flipdot_out:
        flipImage=FlipdotImage(prepareMatrixForAPI(pixel_matrix, sizex, sizey))
        addText(flipImage, sizex, sizey)
        flipdot_matrix.show(flipImage)
    if console_out:
        printToConsole(pixel_matrix, sizex, sizey)

def step(old_pixel_matrix, sizex, sizey):
    """
    Should return a new pixel matrix to be shown in the next loop iteration
    """

    # Your code here

    pass

def addText(flipImage, sizex, sizey):
    """
    You can use flipImage.blitTextAtPosition(string, xPos, yPos) to show text.
    E.g. flipImage.blitTextAtPosition("Hello World!", 10, int(sizey/2))
    """

    # Your code here

    pass

def doSomething(sizex, sizey, udpHostsAndPorts = [], console_out = True, api_defaults = False, update_interval = 0, clean_all = False):
    if len(udpHostsAndPorts) != 0:
        flipdot_matrix = FlipdotMatrix(udpHostsAndPorts, (sizex, sizey))
        flipdot_out = True
    elif api_defaults:
        flipdot_matrix = FlipdotMatrix(imageSize=(sizex,sizey))
        flipdot_out = True
    else:
        flipdot_matrix = None
        flipdot_out = False

    if clean_all == True:
        clean_flipdot(sizex, sizey, flipdot_matrix, flipdot_out, console_out)
        return

    pixel_matrix = generateEmptyMatrix(sizex, sizey)



    # Your code here
    for x in range(sizex):
        pixel_matrix[x][sizey-1] = 1


    show(pixel_matrix, flipdot_matrix, flipdot_out, console_out, sizex, sizey)

def clean_flipdot(sizex, sizey, flipdot_matrix, flipdot_out, console_out):
    pixel_matrix = generateEmptyMatrix(sizex, sizey)
    show(pixel_matrix, flipdot_matrix, flipdot_out, console_out, sizex, sizey)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Introduction to programming with Python')
    parser.add_argument('--sizex', type=int, default=144, help='Size on the x axis')
    parser.add_argument('--sizey', type=int, default=120, help='Size on the y axis')
    parser.add_argument('--console-out', '-c', action='store_true', help='Print matrix to console')
    parser.add_argument('--clean', action='store_true', help='Clean the Flipdot')
    parser.add_argument('--use-api-defaults', '-d', action='store_true', help='Use the default Flipdot host/port data from FlipdotAPI')
    parser.add_argument('--update-interval', '-i', type=float, default=1, help='Interal in seconds between updating the Flipdot panels')
    parser.add_argument('flipdotpanels', nargs='*', help='List of ip46:port strings for the Flipdot panels')
    args = parser.parse_args()

    hostsAndPorts = []
    for ipPort in args.flipdotpanels:
        ipPort = ipPort.replace("[","").replace("]","").rsplit(':',1)
        ipPort = (ipPort[0],int(ipPort[1]))
        hostsAndPorts.append(ipPort)

    #main_loop(args.sizex, args.sizey, udpHostsAndPorts = hostsAndPorts, console_out = args.console_out,
    #        api_defaults = args.use_api_defaults, update_interval = args.update_interval)
    doSomething(args.sizex, args.sizey, udpHostsAndPorts = hostsAndPorts, console_out = args.console_out,
            api_defaults = args.use_api_defaults, update_interval = args.update_interval, clean_all = args.clean)
