#include "translate.h"
#include "config.h"
#include <string.h>
#include <stdint.h>

static int get_bit(uint8_t *data, int bit)
{
    return data[bit/8] & 1 << (7- (bit % 8));
}

static void set_bit(uint8_t *data, int bit)
{
    data[bit/8] |= 1 << (7- (bit % 8));
}

void translate(uint8_t *in, uint8_t *out, int n)
{
    memset(out, 0, n);
    for(int i = 0; i < n * 8; i++) {
        if(get_bit(in, i)) {
            int x = i % XL;
            int y = i / XL;
            set_bit(out, (x%16)*YP+(x/16)*YL+YL-1-y);
        }
    }
}

