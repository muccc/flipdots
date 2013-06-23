Software for some flipdot pannels we have.

http://wiki.muc.ccc.de/flipdot:start


ethersex-flipdot is a submodule which contains
firmware to receive and display data via ethernet.

netfbd is a submodule which contains a daemon
to grab parts of a linux framebuffer and send
via ethernet to the flipdots.

To init these submodules run 'git submodule init'
and 'git submodule update'.

When updating the repository, make sure to also run
'git submodule init' again, to get the lastest
changes inside the submodules.

scripts/ contains support scripts to send raw
test data to the flipdots.


