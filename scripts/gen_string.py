import sys
from FlipdotAPI.FlipdotMatrix import FlipdotMatrix

matrix = FlipdotMatrix()
while True:
    text = sys.stdin.readline().decode('utf-8')
    if text == "":
        break
    matrix.showText(text, True)
