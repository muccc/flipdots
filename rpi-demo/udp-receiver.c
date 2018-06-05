#include "flipdot.h"
#include "flipdot_net.h"
#include "translate.h"
#include "config.h"
#include <stdio.h>
#include <stdbool.h>
#include <signal.h>
#include <stdlib.h>

static bool keepRunning = true;

void intHandler(int x) {
    keepRunning = false;
}

int main(void)
{
    bool init = false;

    struct sigaction act;
    act.sa_handler = intHandler;
    sigaction(SIGINT, &act, NULL);

    flipdot_net_init();
    flipdot_init();
    
    uint8_t data[MODULE_BYTE_COUNT * CONFIG_BUS_LENGTH];
    uint8_t data_trans[MODULE_BYTE_COUNT * CONFIG_BUS_LENGTH];

    while (keepRunning) {
        int n = flipdot_net_recv_frame((uint8_t *)data, sizeof(data));
        if(n <= 0) {
            break;
        }

        if(!init) {
            init=true;
            flipdot_init();
        }
        
        printf("got %u bytes\n", n);

        flipdot_power_on();
        if(n > sizeof(data)) {
            n = sizeof(data);
        }

        translate(data, data_trans, n);
        flipdot_data(data_trans, n);

        flipdot_power_off();
    }
    return 0;
}
