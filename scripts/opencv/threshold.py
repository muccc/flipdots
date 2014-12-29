#!/usr/bin/python2
import numpy as np
import cv2
import socket,time,math

cap = cv2.VideoCapture(0)


sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)

FD_LEFT="2001:67c:20a1:1095:c49d:e22d:6891:dcd"
FD_MIDDLE="2001:67c:20a1:1095:34b1:6957:8ddb:3a79"
FD_RIGHT="2001:67c:20a1:1095:552a:1594:871f:d9c2"

UDPPORT=2323

IMG_THRESHOLD=64



def send(image,dest):
    msg = '';
    pieces = '';
    for line in image:
        pieces += ''.join(str(x) for x in line)
    
    pieces = [pieces[i:i+8] for i in range(0, len(pieces), 8)]
    
    for i in pieces:
        if (len(i) < 8):
            i = i.ljust(8, '1')
        msg += chr(int(str(i), 2))

    sock.sendto(msg, (dest, UDPPORT))

def partition(img):
    rows,cols = img.shape

    dst = cv2.transpose(img)
    
    cv2.imshow("rot",dst)

    left = dst[0:cols/3,0:rows]
    middle = dst[cols/3+1:2*cols/3,0:rows]
    right = dst[2*cols/3+1:cols,0:rows]

#    left = img[0:img.shape[0],0:img.shape[1]/3]
#    middle = img[0:img.shape[0],img.shape[1]/3+1:2*img.shape[1]/3]
#    right = img[0:img.shape[0],2*img.shape[1]/3+1:img.shape[1]]
    return left,middle,right




while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()
    
    dim=(144,120)
    resized=cv2.resize(frame,dim)
    
    resized = cv2.flip(resized,0)

    # Our operations on the frame come here
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

    ret,thresh = cv2.threshold(gray,IMG_THRESHOLD,1,cv2.THRESH_BINARY) 

    # Display the resulting frame
    cv2.imshow('frame',gray)
    cv2.imshow('canny',thresh*255)
    left,middle,right = partition(thresh)
    send(left,FD_LEFT)
    send(middle,FD_MIDDLE)
    send(right,FD_RIGHT)
    cv2.imshow("left",left*255)
    cv2.imshow("middle",middle*255)
    cv2.imshow("right",right*255)
   
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    time.sleep(0.55)

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
