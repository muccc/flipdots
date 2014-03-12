This code is used to control flipdots using a Raspberry Pi.

It is designed to work with the board which can be be found in
the board/ directory in the parent folder.

First compile and install the simplespi and max7301 libraries
in the parent folder.

Then edit config.h to match you setup. You have to define how
many independent buses and how many panels per bus are connected
to the board.

You can now start the udp-receiver program. It will listen for
UDP packets on port 2323. It will simply display the binary
stream of data contained in the packets.

It will display the MSB of the first byte of the packet in
the lower left corner of bus A. It will continue to fill the
column until it reaches the top. It will continue at the
bottom of the second column of bus A. After reaching the
top of the last column of bus A, it will continue with lower
left corner of bus B.

With each new packet, it will start again at the lower left
corner of bus A.

