#!/usr/bin/env python
import socket
import sys

s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
s.bind(('::', 2323,0,0))
s.listen(1)

conn, addr = s.accept()
f = open(sys.argv[1], 'w')

while 1:
    data = conn.recv(1024)
    if not data: break
    f.write(data)

conn.close()
f.close()

