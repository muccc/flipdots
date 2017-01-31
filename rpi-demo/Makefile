CFLAGS = -O3 -Wall -Werror -std=c99
LIBS = -lbcm2835

all: demo udp-receiver

flipdot.o: flipdot.c flipdot.h config.h
	$(CC) $(CFLAGS) -c flipdot.c -o flipdot.o

demo: flipdot.o demo.c
	$(CC) $(CFLAGS) demo.c flipdot.o $(LIBS) -o demo

udp-receiver: flipdot_net.o flipdot.o udp-receiver.c config.h
	$(CC) $(CFLAGS) udp-receiver.c flipdot.o flipdot_net.o $(LIBS) -o udp-receiver

flipdot_net.o: flipdot_net.c flipdot_net.h
	$(CC) $(CFLAGS) -c flipdot_net.c -o flipdot_net.o


clean:
	rm -f *.o demo
.PHONY:
	clean all
