#include "max7301.h"
#include <stdbool.h>
#include <stdio.h>

int main(void)
{
    max7301_init(100, false);

    int i, j;
    for(i = 4; i < 32; i++) {
        max7301_set_pin_as_output(i);
    }
    //max7301_set_pin_as_input(31, false);
    //printf("Pin 31 = %d\n", max7301_get_pin(31));
    
    while (1) {
        for(j = 0; j < 7; j++) {
            for(i = 4; i < 32; i++) {
                max7301_set_pin(i, 1);
            }
            max7301_step();
            for(i = 4; i < 32; i++) {
                max7301_set_pin(i, 0);
            }
            max7301_step();
        }
        max7301_flush_history();
    }
}
