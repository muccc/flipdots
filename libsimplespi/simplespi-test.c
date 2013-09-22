#include "simplespi.h"
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

int main(void)
{
    int i;
    uint8_t array[256][2];

    simplespi_init();
     
    for (i = 0; i < 256; i++) {
        array[i][0] = i;
        array[i][1] = i + 1;
    }

    while (1) {
        simplespi_write_read((uint8_t *)"fx", 2, false);
        simplespi_write_read_list(&array[0][0], 256, 2, false);
    }
}

