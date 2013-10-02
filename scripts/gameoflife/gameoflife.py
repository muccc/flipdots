import socket, time, sys
from random import randint



UDPHOST="2001:7f0:3003:cafe:ba27:ebff:fe71:dd32"
#UDPHOST="fe80::221:6bff:fe4c:6e7c"
UDPPORT=2323

SIZE_Y = 120
SIZE_X = 48
DELAY =0.5 

#SEEDFILE="lightweight_spaceship"
SEEDFILE="glider"
#SEEDFILE="pulsar"

sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)

def randomUniverse():
    """
    populates a universe with random state cells
    returns following datastructure:
    [
    [1,0,1,0,0,0,1...]
    [0,1,1,0,1,...]
    [0,1,1,1,0,0,...]
    ]
    """
    universe = []
    for x in range ( 0 , SIZE_X ):
        universe.append( [] )
        for y in range ( 0 , SIZE_Y ):
            universe[x].append( randint(0,1) )
    return universe

def loadUniverse(seedfile):
    """
    loads a universe from file and fills the rest
    of the available space with dead cells
    """
    #create empty universe
    universe = []
    for x in range (0 ,SIZE_X ):
        universe.append( [] )
        for y in range ( 0 , SIZE_Y  ):
            universe[x].append( 0 )

    #load seed
    try:
        seedfile = open (seedfile)
    except:
        print "Could not open seed file. Check Speeling and permissions."

    seed = []
    try:
        while True:
            seed.append(list(seedfile.next().splitlines()))
    except:
        seedfile.close()

    mid_x  = SIZE_X / 2
    mid_y  = SIZE_Y / 2
    seed_x = len(seed)
    seed_y = len(seed[0][0])

    for x in range (0, seed_x):
        for y in range (0, seed_y):
            universe[mid_x+x-(seed_x/2)][mid_y+y-(seed_y/2)]=int(seed[x][0][y])

    return universe


def updateUniverse(universe):
    """
    updates the cellstates of a universe to the next itaration

    """
    newUniverse=randomUniverse()
    for x in range(0, SIZE_X):
        for y in range(0, SIZE_Y):
            neighborhood = 0
            cell = universe[x][y]
            for i in range(x-1,x+2):
                for j in range (y-1,y+2):
                    neighborhood += universe[i % SIZE_X][j % SIZE_Y]
            neighborhood = neighborhood -cell
            #cell is alive
            if (cell == 1 ):
                #less than 2 or more than 3 neighbors: die
                if ( neighborhood < 2 or neighborhood > 3 ):
                    newUniverse[x][y] = 0
                else:
                    newUniverse[x][y] = 1
            #cell is dead
            else :
                #3 neighnors: become alive
                if ( neighborhood == 3):
                    newUniverse[x][y] = 1
                else:
                    newUniverse[x][y] = 0

#    print "\n"
#    print universe
#    print newUniverse
    return newUniverse




def send(image):
	msg = '';
	pieces = '';
	for line in image:
		pieces += ''.join(str(x) for x in line)

	pieces = [pieces[i:i+8] for i in range(0, len(pieces), 8)]

	for i in pieces:
		if (len(i) < 8):
			i = i.ljust(8, '1')
		msg += chr(int(str(i), 2))

	sock.sendto(msg, (UDPHOST, UDPPORT))

def make_buffer(universe):

    buffer = []
    for x in range(0,len(universe)):
        buffer.append([])
        for y in range(0, len(universe[x])):
            buffer[x].append(universe[x][y])
    return buffer

def initGOL():
    if len(sys.argv) == 2:
        if sys.argv[1]=="random":
            return randomUniverse()
        else:
            try:
                with open(sys.argv[1]):pass
            except IOError:
                print "Seedfile not found. Check filename and path."
                sys.exit(0)
            return loadUniverse(sys.argv[1])
    else:
        print ("\n  Usage:\n"
               "       python gameoflife.py random       #load a random universe\n"
               "       python gameoflife.py <seedfile>   #load a seedfile\n"
               "\n")
        sys.exit(0)
        






def main():
    i = 0
    u = initGOL()
#    u=randomUniverse()
#    u=loadUniverse(SEEDFILE)
    while True:
        b=make_buffer(u)
        send(b)
        time.sleep(DELAY)
        u = list(updateUniverse(u))
main()


