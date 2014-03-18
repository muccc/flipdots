#include "flipdot.h"
#include "flipdot_net.h"
#include <stdio.h>
#include <stdbool.h>
#include <sys/time.h>
#include "time-helper.h"

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
        struct timeval t0, t1;
        gettimeofday(&t0, NULL);

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
        gettimeofday(&t1, NULL);
        printf("Total time: %lu ms\n", time_diff(t0,t1)/1000);
        printf("Col time: %lu ms\n", col_time/1000);
        printf("Row time: %lu ms\n", row_time/1000);
        printf("Strobe time: %lu ms\n", strobe_time/1000);
        col_time = row_time = strobe_time = 0;
    }
    return 0;
}

