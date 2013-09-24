CFLAGS = -O3 -Wall -Werror -std=c99
LIBS = -lmax7301 -lsimplespi

all: demo

flipdot.o: flipdot.c flipdot.h
	$(CC) $(CFLAGS) -c flipdot.c -o flipdot.o

demo: flipdot.o demo.c
	$(CC) $(CFLAGS) demo.c flipdot.o $(LIBS) -o demo

clean:
	rm -f *.o demo
.PHONY:
	clean all
