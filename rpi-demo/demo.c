#include "flipdot.h"
extern int active_pinning;
int main(void)
{
    flipdot_init();
    
    uint8_t data[2*20*7];
    uint8_t d = 0; 
    while (1) {
        int i;
        for (i = 0; i < sizeof(data); i++) {
            data[i] = d;
        }
        //d = 255 - d;
        d++;
        for(i = 1; i < 4; i++) {
            active_pinning = i;
            flipdot_data(data, sizeof(data));
        }
        //volatile uint32_t x;
        //for(x=0; x<10000000; x++);
        //for(x=0; x<10000000; x++);
        //for(x=0; x<10000000; x++);
        //for(x=0; x<10000000; x++);
    }
    return 0;
}
