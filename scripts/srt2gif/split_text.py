import extents
import sys
import collections

MAX_PIXLES = 96

text = open(sys.argv[1]).read()
#size = int(sys.argv[2])
size = 10


text = text.replace('\n', ' ')
text = text.split()

text = collections.deque(text)


while len(text) > 0:
    words = collections.deque()

    while True:
        words.append(text.popleft())
        line = ' '.join(words)

        if extents.get_size(line, 'sans', size)[0] > MAX_PIXLES:
            if len(words) > 1:
                text.appendleft(words.pop())
            else:
                print "-------->", 
            print ' '.join(words)
            break

