CFLAGS = -O3 -Wall -Werror -std=c99
LIBS = -lmax7301 -lsimplespi

all: udp-receiver

flipdot.o: flipdot.c flipdot.h
	$(CC) $(CFLAGS) -c flipdot.c -o flipdot.o

time-helper.o: time-helper.c time-helper.h
	$(CC) $(CFLAGS) -c time-helper.c -o time-helper.o

udp-receiver: flipdot_net.o flipdot.o udp-receiver.c time-helper.o
	$(CC) $(CFLAGS) udp-receiver.c flipdot.o time-helper.o flipdot_net.o $(LIBS) -o udp-receiver

flipdot_net.o: flipdot_net.c flipdot_net.h
	$(CC) $(CFLAGS) -c flipdot_net.c -o flipdot_net.o


clean:
	rm -f *.o demo
.PHONY:
	clean all
