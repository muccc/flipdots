CFLAGS = -O3 -Wall -Werror

all: libsimplespi.a simplespi-test

simplespi.o: simplespi.c simplespi.h
	$(CC) $(CFLAGS) -c simplespi.c -o simplespi.o

simplespi-test: simplespi.o simplespi-test.c
	$(CC) $(CFLAGS) simplespi-test.c simplespi.o -o simplespi-test

libsimplespi.a: simplespi.o
	$(AR) rcs libsimplespi.a simplespi.o

clean:
	rm -f *.o simplespi-test

install: libsimplespi.a
	cp libsimplespi.a /usr/local/lib
	cp simplespi.h /usr/local/include

.PHONY:
	clean all install
