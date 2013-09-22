#ifndef SPI_H
#define SPI_H

#include <stdint.h>
#include <stdbool.h>

int simplespi_close();
int simplespi_write_read(uint8_t *data, int length, bool do_rx);
int simplespi_write_read_list(uint8_t *data, int n, int length, bool do_rx);
int simplespi_init(void);

#endif

