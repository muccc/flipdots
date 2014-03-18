#include "flipdot.h"
#include "flipdot_net.h"
#include <stdio.h>
#include <stdbool.h>
#include <sys/time.h>

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

        flipdot_data(data, sizeof(data[0]), 3);

        gettimeofday(&t1, NULL);
        t1.tv_sec -= t0.tv_sec;
        t0.tv_sec = 0;

        int t = (t1.tv_sec * 1000000UL + t1.tv_usec) - t0.tv_usec;

        printf("Total time: %u ms\n", t/1000);
    }
    return 0;
}

