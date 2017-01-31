#include "flipdot.h"
#include "flipdot_net.h"
#include "config.h"
#include <stdio.h>
#include <stdbool.h>

extern int active_pinning;
int main(void)
{
    bool init = false;
    flipdot_net_init();
    flipdot_init();
    
    uint8_t data[CONFIG_BUS_COUNT][MODULE_BYTE_COUNT * CONFIG_BUS_LENGTH];
    while (1) {
        int n = flipdot_net_recv_frame((uint8_t *)data, sizeof(data));
        if(!init) {
            init=true;
            flipdot_init();
        }
        
        printf("got %u bytes\n", n);
        int i;
        for(i = 0; i < CONFIG_BUS_COUNT; i++) {
            // This is supper uggly, but there is a global variable
            // which selects the active bus (A, B, C, D)...

            active_pinning = i;
            if(n >= sizeof(data[0])) {
                flipdot_data(data[i], sizeof(data[0]));
                n -=  sizeof(data[0]);
            } else {
                flipdot_data(data[i], n);
                // There is no more data to consume
                break;
            }
        }
    }
    return 0;
}
