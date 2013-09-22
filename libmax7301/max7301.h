#ifndef MAX7301_H
#define MAX7301_H

#include <stdint.h>
#include <stdbool.h>
void max7301_init(int max_history_size, bool debug);
void max7301_step(void);
void max7301_flush_history(void);
void max7301_set_pin_as_output(int pin);
void max7301_set_pin(int pin, int value);
void max7301_set_pin_as_input(int pin, bool pullup);
int max7301_get_pin(int pin);

#endif

