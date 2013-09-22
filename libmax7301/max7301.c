#include "max7301.h"
#include <simplespi.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <stdio.h>

static int get_conf_register_for_pin(int pin);
static int get_value_register_for_pin(int pin);
static int read_register(int reg);
static int write_register(uint8_t reg, uint8_t data);
static int get_bit_shift_for_pin(int pin);
static int get_base_register_for_pin(int pin);

#define PIN_COUNT    32

typedef struct {
    int value;
    bool tainted;
} pin_t;

pin_t (*pins_history)[PIN_COUNT];
static int history_size;
static int history_count;
#define pins    (pins_history[history_count-1])

static uint8_t *transfers_list;
static bool debug_active;

#define DEBUG(...)  if(debug_active) printf(__VA_ARGS__);

void max7301_init(int max_history_size, bool debug)
{
    simplespi_init();
    debug_active = debug;

    // turn on
    write_register(0x04, 0x01);
    history_size = max_history_size;
    
    pins_history = malloc(sizeof(pins_history[0]) * history_size);
    transfers_list = malloc(history_size * 4 * 2);

    history_count = 1;

    int pin;
    for (pin = 0; pin < PIN_COUNT; pin++) {
        pins[pin].value = 0; //max7301_get_pin(pin);
        pins[pin].tainted = false;
    }
}

void max7301_set_pin_as_output(int pin)
{
    int reg = get_conf_register_for_pin(pin);
    int content = read_register(reg);
    content &= ~(0x3 << get_bit_shift_for_pin(pin));
    content |= 0x01 << get_bit_shift_for_pin(pin);
    write_register(reg, content);
}

void max7301_set_pin(int pin, int value)
{
    DEBUG("max7301_set_pin(%d, %d)\n", pin, value);
    if (pins[pin].value != value) {
        pins[pin].value = value;
        DEBUG("tainting pin.\n");
        pins[pin].tainted = true;
    }
}

void max7301_step(void)
{
    DEBUG("max7301_step()\n");
    DEBUG("history_count = %d\n", history_count);
    pin_t (*old_pins)[PIN_COUNT] = &pins;
    if (history_count == history_size) {
        DEBUG("history full. flushing\n");
        max7301_flush_history();
    } else {
        history_count++;
        DEBUG("history := %d\n", history_count);

        int pin;
        for (pin=0; pin < PIN_COUNT; pin++) {
            DEBUG("forwarding state of pin %d to %d\n", pin, (*old_pins)[pin].value);
            pins[pin].value = (*old_pins)[pin].value;
            pins[pin].tainted = false;
        }
    }
}

void max7301_flush_history(void)
{
    int i, pin, j, data;
    int transfers_count = 0;

    DEBUG("max7301_flush_history()\n");
    for (i = 0; i < history_count; i++) {
        for (pin = 0; pin < PIN_COUNT; pin++) {
            if (pins_history[i][pin].tainted) {
                DEBUG("[%d][%d] is tainted\n", i, pin);
                DEBUG("transfers_list[%d] := %d\n", transfers_count, get_base_register_for_pin(pin));
                transfers_list[transfers_count++] = get_base_register_for_pin(pin);
                data = 0;
                for (j = 0; j < 8; j++) {
                    DEBUG("rotating data\n");
                    data >>= 1;
                    DEBUG("data = %d\n", data);
                    if (pin < PIN_COUNT) {
                        if (pins_history[i][pin++].value) {
                            DEBUG("[%d][%d] will be set\n", i, pin-1);
                            DEBUG("setting MSB of data\n");
                            data |= 0x80;
                            DEBUG("data = %d\n", data);
                        }
                    }
                }
                // We have not yet looked at this pin and the for loop
                // will increment pin again, so we have to decrement pin
                // here first.
                pin--;

                DEBUG("transfers_list[%d] := %d\n", transfers_count, data);
                transfers_list[transfers_count++] = data;
            }
        }
    }
    DEBUG("sending list with %d transfers to spi interface.\n", transfers_count / 2);
    for (i = 0; i < transfers_count; i +=2 ) {
        DEBUG("%02x %02x ", transfers_list[i], transfers_list[i+1]);
    }
    DEBUG("\n");
    simplespi_write_read_list(transfers_list, transfers_count / 2, 2, false);

    DEBUG("resetting history\n");
    for (pin = 0; pin < PIN_COUNT; pin++) {
        DEBUG("setting state of pin %d to %d\n", pin, pins[pin].value);
        pins_history[0][pin].value = pins[pin].value;
        pins_history[0][pin].tainted = false;
    }
    DEBUG("history_count := 1\n");
    history_count = 1;
}

void max7301_set_pin_as_input(int pin, bool pullup)
{
    int reg = get_conf_register_for_pin(pin);
    int content = read_register(reg);
    content &= ~(0b11 << get_bit_shift_for_pin(pin));
    if (pullup) {
        content |= 0x3 << get_bit_shift_for_pin(pin);
    } else {
        content |= 0x2 << get_bit_shift_for_pin(pin);
    }
    write_register(reg, content);
}

int max7301_get_pin(int pin)
{
    int reg = get_value_register_for_pin(pin);
    int value = read_register(reg);
    return value & 0x01;
}
 
static int get_conf_register_for_pin(int pin)
{
    return (pin-4)/4 + 0x09;
}

static int get_value_register_for_pin(int pin)
{
    return 0x20 + pin;
}

static int get_base_register_for_pin(int pin)
{
    return 0x40 + pin;
}

static int read_register(int reg)
{
    write_register(0x80 | reg, 0);
    return write_register(0x80, 0x00);
}

static int write_register(uint8_t reg, uint8_t data)
{
    uint8_t buf[2] = {reg, data};
    simplespi_write_read(buf, 2, true);
    return buf[1];
}

static int get_bit_shift_for_pin(int pin)
{
    return ((pin % 4) * 2);
}

/*
    for (i = 0; i < 256; i++) {
        array[i][0] = i;
        array[i][1] = i + 1;
    }

    while (1) {
        simplespi_write_read((uint8_t *)"fx", 2, false);
        simplespi_write_read_list(&array[0][0], 256, 2, false);
    }
}
*/


