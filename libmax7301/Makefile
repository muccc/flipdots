CFLAGS = -O3 -Wall -Werror
LIBS = -lsimplespi

all: libmax7301.a max7301-test

max7301.o: max7301.c max7301.h
	$(CC) $(CFLAGS) -c max7301.c -o max7301.o

max7301-test: max7301.o max7301-test.c
	$(CC) $(CFLAGS) max7301-test.c max7301.o $(LIBS) -o max7301-test

libmax7301.a: max7301.o
	$(AR) rcs libmax7301.a max7301.o

clean:
	rm -f *.o max7301-test *.a

install: libmax7301.a
	cp libmax7301.a max7301.h /usr/local/lib

.PHONY:
	clean all install
