#include "flipdot.h"
#include "flipdot_net.h"
#include <stdio.h>
#include <stdbool.h>

extern int active_pinning;
int main(void)
{
    bool init = false;
    flipdot_net_init();
    
    uint8_t data[3][2*20*6];
    while (1) {
        int n = flipdot_net_recv_frame((uint8_t *)data, sizeof(data));
        if(!init) {
            init=true;
            flipdot_init();
        }
        
        printf("got %u bytes\n", n);
        int i;
        for(i = 1; i < 4; i++) {
            active_pinning = i;
            if(n >= sizeof(data[0])) {
                flipdot_data(data[i-1], sizeof(data[0]));
                n -=  sizeof(data[0]);
            } else {
                flipdot_data(data[i-1], n);
                break;
            }
        }
    }
    return 0;
}
