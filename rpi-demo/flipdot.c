/*
* Copyright (c) 2013 Franz Nord
*
* This program is free software; you can redistribute it and/or
* modify it under the terms of the GNU General Public License
* as published by the Free Software Foundation; either version 3
* of the License, or (at your option) any later version.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with this program; if not, write to the Free Software
* Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
*
* For more information on the GPL, please go to:
* http://www.gnu.org/copyleft/gpl.html
*/

#include "flipdot.h"
#include "config.h"

#include <bcm2835.h>
#include <time.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <stdbool.h>
#include <unistd.h>
#include <inttypes.h>
#include <stdio.h>

//extern int usleep (__useconds_t __useconds);
//#define _delay_us(x) usleep(x)
#define _delay_us(x) bcm2835_delayMicroseconds(x)


#define ISBITSET(x,i) ((x[i>>3] & (1<<(i&7)))!=0)
#define SETBIT(x,i) x[i>>3]|=(1<<(i&7));

#define DATA(reg)								\
	((reg == ROW) ? pinning[active_pinning].data_row : pinning[active_pinning].data_col)
#define CLK(reg)								\
	((reg == ROW) ? pinning[active_pinning].clk_row : pinning[active_pinning].clk_col)

static uint8_t buffer_a[CONFIG_BUS_COUNT][DISP_BYTE_COUNT];
static uint8_t buffer_b[CONFIG_BUS_COUNT][DISP_BYTE_COUNT];
static uint8_t buffer_to_0[CONFIG_BUS_COUNT][DISP_BYTE_COUNT];
static uint8_t buffer_to_1[CONFIG_BUS_COUNT][DISP_BYTE_COUNT];
static uint8_t *buffer_new[CONFIG_BUS_COUNT], *buffer_old[CONFIG_BUS_COUNT];

static void sreg_push_bit(enum sreg reg, uint8_t bit);
static void sreg_fill(enum sreg reg, uint8_t *data, int count);
static void sreg_fill_row(uint8_t *data, int count);
static void sreg_fill_col(uint8_t *data, int count);

static void strobe(void);
static void flip_white_start(void);
static void flip_white_stop(void);
static void flip_black_start(void);
static void flip_black_stop(void);

uint8_t diff_to_0(uint8_t old, uint8_t new);
uint8_t diff_to_1(uint8_t old, uint8_t new);

static void map_two_buffers(uint8_t (*fun)(uint8_t, uint8_t), uint8_t a[], uint8_t b[], uint8_t dst[], unsigned int count);

static void display_frame_differential(uint8_t *to_0, uint8_t *to_1);

// XXX: Change to symbolic defines like RPI_V2_GPIO_P1_03
flipdot_pinning pinning[CONFIG_BUS_COUNT] =
{
    {.data_col = RPI_V2_GPIO_P1_03, .data_row = RPI_V2_GPIO_P1_05, .strobe = RPI_V2_GPIO_P1_12, .oe_white = RPI_V2_GPIO_P1_13, .oe_black = RPI_V2_GPIO_P1_18, .clk_col = RPI_V2_GPIO_P1_22, .clk_row = RPI_V2_GPIO_P1_23},
    //{.data_col = RPI_V2_GPIO_P1_03, .data_row = RPI_V2_GPIO_P1_07, .strobe = RPI_V2_GPIO_P1_12, .oe_white = RPI_V2_GPIO_P1_15, .oe_black = RPI_V2_GPIO_P1_19, .clk_col = RPI_V2_GPIO_P1_22, .clk_row = RPI_V2_GPIO_P1_23},
    //{.data_col = RPI_V2_GPIO_P1_03, .data_row = RPI_V2_GPIO_P1_11, .strobe = RPI_V2_GPIO_P1_12, .oe_white = RPI_V2_GPIO_P1_16, .oe_black = RPI_V2_GPIO_P1_21, .clk_col = RPI_V2_GPIO_P1_22, .clk_row = RPI_V2_GPIO_P1_23},
};

static uint8_t flipper[256];

static uint8_t reverse(uint8_t b)
{
    b = (b & 0xF0) >> 4 | (b & 0x0F) << 4;
    b = (b & 0xCC) >> 2 | (b & 0x33) << 2;
    b = (b & 0xAA) >> 1 | (b & 0x55) << 1;
    return b;
}
int active_pinning = 0;

int
flipdot_init(void)
{
    //bcm2835_set_debug(1);
    if (!bcm2835_init())
        return 1;

	/* init pins */
    int i;
    for(i = 0; i < CONFIG_BUS_COUNT; i++) {
        active_pinning = i;
        bcm2835_gpio_fsel(pinning[i].data_col, BCM2835_GPIO_FSEL_OUTP);
        bcm2835_gpio_fsel(pinning[i].data_row, BCM2835_GPIO_FSEL_OUTP);
        bcm2835_gpio_fsel(pinning[i].strobe, BCM2835_GPIO_FSEL_OUTP);
        bcm2835_gpio_fsel(pinning[i].oe_white, BCM2835_GPIO_FSEL_OUTP);
        bcm2835_gpio_fsel(pinning[i].oe_black, BCM2835_GPIO_FSEL_OUTP);
        bcm2835_gpio_fsel(pinning[i].clk_col, BCM2835_GPIO_FSEL_OUTP);
        bcm2835_gpio_fsel(pinning[i].clk_row, BCM2835_GPIO_FSEL_OUTP);

        /* Init buffer pointers */
        buffer_new[active_pinning] = buffer_a[active_pinning];
        buffer_old[active_pinning] = buffer_b[active_pinning];

        /* Synchronize buffers and flipdot pixel state */
        memset(buffer_new[active_pinning], 0xFF, DISP_BYTE_COUNT);
        memset(buffer_old[active_pinning], 0x00, DISP_BYTE_COUNT);
        flipdot_data(buffer_old[active_pinning], DISP_BYTE_COUNT);
        flipdot_data(buffer_old[active_pinning], DISP_BYTE_COUNT);
        flipdot_data(buffer_old[active_pinning], DISP_BYTE_COUNT);
    }

    for(i=0; i<256; i++) {
        flipper[i] = reverse(i);
    }
    
    return 0;
}

void
flipdot_data(uint8_t *frame, uint16_t size)
{
	uint8_t *tmp;

	memcpy(buffer_old[active_pinning], frame, size); /* Copy frame into buffer with old data */
    
    int i;
	for(i = 0; i < size; i++) {
        uint8_t c = buffer_old[active_pinning][i];
        buffer_old[active_pinning][i] = flipper[c];
    }

	tmp = buffer_old[active_pinning];				 /* swap pointers buffer_new[active_pinning] and buffer_old[active_pinning] */
	buffer_old[active_pinning] = buffer_new[active_pinning];
	buffer_new[active_pinning] = tmp;
	
	map_two_buffers(diff_to_0, buffer_old[active_pinning], buffer_new[active_pinning], buffer_to_0[active_pinning], DISP_BYTE_COUNT);
	map_two_buffers(diff_to_1, buffer_old[active_pinning], buffer_new[active_pinning], buffer_to_1[active_pinning], DISP_BYTE_COUNT);

	display_frame_differential(buffer_to_0[active_pinning], buffer_to_1[active_pinning]);
}

static void
map_two_buffers(uint8_t (*fun)(uint8_t, uint8_t), uint8_t a[], uint8_t b[], uint8_t dst[], unsigned int count) {
	for (int i = 0; i < count; ++i) {
		dst[i] = fun(a[i], b[i]);
	}
}

uint8_t
diff_to_0(uint8_t old, uint8_t new) {
	return old & ~new;
}

uint8_t
diff_to_1(uint8_t old, uint8_t new) {
	return ~(~old & new);
}

#if 1

static uint64_t timer;

static uint64_t
get_time(void)
{
    struct timespec time;
    clock_gettime(CLOCK_MONOTONIC_RAW, &time);
    uint64_t time_us = time.tv_sec * 1000000 + time.tv_nsec / 1000;
    return time_us;
}

static void
timer_start(void)
{
    timer = get_time();
}

static void
timer_wait(uint32_t micros)
{
    if(micros == 0) {
        return;
    }

    uint64_t elapsed = get_time() - timer;
    if(micros > elapsed) {
        _delay_us(micros - elapsed);
    } else {
        printf("Too slow: %" PRIu64 "/%" PRIu32 "\n", elapsed, micros);
    }
}

static void
display_frame_differential(uint8_t *to_0, uint8_t *to_1)
{
	uint8_t row_select[DISP_ROWS/8];
	int row;
	uint8_t *row_data_to_0, *row_data_to_1;

	// Select the first row
	row = 0;	
	memset(row_select, 0, DISP_ROWS/8);
	SETBIT(row_select, row);			   /* Set selected row */
	sreg_fill(COL, row_select, DISP_ROWS); /* Fill row select shift register */

	// Pre-fill the data for row 0
	row_data_to_0 = to_0 + row * DISP_COLS/8;
	sreg_fill(ROW, row_data_to_0, DISP_COLS); /* Fill row to 0 shift register */

	while(row < DISP_ROWS) {
		// Apply the shift register content for the black pixels
		strobe();
		flip_black_start();

		row_data_to_1 = to_1 + row * DISP_COLS/8;
		sreg_fill(ROW, row_data_to_1, DISP_COLS); /* Fill row to 1 shift register */

		flip_black_stop();
		// Apply the shift register content for the white pixels
		strobe();
		flip_white_start();

		// Move one row further
		sreg_push_bit(COL, 0);
		row_data_to_0 = to_0 + (row+1) * DISP_COLS/8;
		sreg_fill(ROW, row_data_to_0, DISP_COLS); /* Fill row to 0 shift register */

		flip_white_stop();
		row++;
	}
}
#else
static void
display_frame_differential(uint8_t *to_0, uint8_t *to_1)
{
	uint8_t row_select[DISP_ROWS/8];

	for (int row = 0; row < DISP_ROWS; ++row) {
		uint8_t *row_data_to_0 = to_0 + row * DISP_COLS/8;
		uint8_t *row_data_to_1 = to_1 + row * DISP_COLS/8;
		
		memset(row_select, 0, DISP_ROWS/8);
		SETBIT(row_select, row);			   /* Set selected row */
		sreg_fill(COL, row_select, DISP_ROWS); /* Fill row select shift register */
		
		sreg_fill(ROW, row_data_to_0, DISP_COLS); /* Fill row to 0 shift register */
		strobe();
		flip_black_start();
		flip_black_stop();

		sreg_fill(ROW, row_data_to_1, DISP_COLS); /* Fill row to 1 shift register */
		strobe();
		flip_white_start();
		flip_white_stop();
	}
}
#endif

/* Output bit on reg and pulse clk signal */
static void
sreg_push_bit(enum sreg reg, uint8_t bit)
{
#ifdef CLK_DELAY
    volatile int i;
#endif
    bcm2835_gpio_write(DATA(reg), bit);
    while(bcm2835_gpio_lev(DATA(reg)) != bit){
        printf("Data error\n");
        bcm2835_gpio_write(DATA(reg), bit);
    }
#ifdef CLK_DELAY
    for(i=0; i<CLK_DELAY; i++);
#endif
    bcm2835_gpio_write(CLK(reg), 1);
    while(!bcm2835_gpio_lev(CLK(reg))){
        printf("Clock set error\n");
        bcm2835_gpio_write(CLK(reg), 1);
    }
#ifdef CLK_DELAY
    for(i=0; i<CLK_DELAY; i++);
#endif
    bcm2835_gpio_write(CLK(reg), 0);
    while(bcm2835_gpio_lev(CLK(reg))){
        printf("Clock clear error\n");
        bcm2835_gpio_write(CLK(reg), 0);
    }
}

static void
sreg_fill(enum sreg reg, uint8_t *data, int count)
{
	switch (reg) {
		case ROW: sreg_fill_row(data, count); break;
		case COL: sreg_fill_col(data, count); break;
	}
}

/* Fill col register with count bits from data LSB first */
static void
sreg_fill_col(uint8_t *data, int count)
{
	int i = 0;
	while (i < count) {
		sreg_push_bit(COL, ISBITSET(data, (count-i-1)));
		++i;
	}
}

/* TODO: generalize for more panels */
static void
sreg_fill_row(uint8_t *data, int count)
{
    /* This is necessary because the row
	* register has 4 unmapped bits */
    int i;
    int bit = 0;

    // Send 4 extra bits at the beginnig
    int c = 20;

    for(i = 0; i < count; i++) {
        if(c == 20) {
            // 20 bits have been pushed, send the 4
            // extra bits now.
            sreg_push_bit(ROW, bit);
            sreg_push_bit(ROW, bit);
            sreg_push_bit(ROW, bit);
            sreg_push_bit(ROW, bit);
            c = 0;
        }
        bit = ISBITSET(data, (count-i-1)) ? 1 : 0;
        /* count-i-1 because the first bit needs to go last */
        sreg_push_bit(ROW, bit);
        c++;
    }	
}

static void
strobe(void)
{
    bcm2835_gpio_write(pinning[active_pinning].strobe, 1);
    while(!bcm2835_gpio_lev(pinning[active_pinning].strobe)){
        bcm2835_gpio_write(pinning[active_pinning].strobe, 1);
    }
	_delay_us(STROBE_DELAY);
    bcm2835_gpio_write(pinning[active_pinning].strobe, 0);
    while(bcm2835_gpio_lev(pinning[active_pinning].strobe)){
        bcm2835_gpio_write(pinning[active_pinning].strobe, 0);
    }
}

static void
flip_white_start(void)
{
    timer_start();
    bcm2835_gpio_write(pinning[active_pinning].oe_black, 0);
    while(bcm2835_gpio_lev(pinning[active_pinning].oe_black)){
        bcm2835_gpio_write(pinning[active_pinning].oe_black, 0);
    }
    bcm2835_gpio_write(pinning[active_pinning].oe_white, 1);
    while(!bcm2835_gpio_lev(pinning[active_pinning].oe_white)){
        bcm2835_gpio_write(pinning[active_pinning].oe_white, 1);
    }
}

static void
flip_white_stop(void)
{
	timer_wait(FLIP_DELAY_WHITE);
    bcm2835_gpio_write(pinning[active_pinning].oe_black, 0);
    while(bcm2835_gpio_lev(pinning[active_pinning].oe_black)){
        bcm2835_gpio_write(pinning[active_pinning].oe_black, 0);
    }
    bcm2835_gpio_write(pinning[active_pinning].oe_white, 0);
    while(bcm2835_gpio_lev(pinning[active_pinning].oe_white)){
        bcm2835_gpio_write(pinning[active_pinning].oe_white, 0);
    }
}

static void
flip_black_start(void)
{
    timer_start();
    bcm2835_gpio_write(pinning[active_pinning].oe_black, 1);
    while(!bcm2835_gpio_lev(pinning[active_pinning].oe_black)){
        bcm2835_gpio_write(pinning[active_pinning].oe_black, 1);
    }
    bcm2835_gpio_write(pinning[active_pinning].oe_white, 0);
    while(bcm2835_gpio_lev(pinning[active_pinning].oe_white)){
        bcm2835_gpio_write(pinning[active_pinning].oe_white, 0);
    }
}

static void
flip_black_stop(void)
{
	timer_wait(FLIP_DELAY_BLACK);
    bcm2835_gpio_write(pinning[active_pinning].oe_black, 0);
    while(bcm2835_gpio_lev(pinning[active_pinning].oe_black)){
        bcm2835_gpio_write(pinning[active_pinning].oe_black, 0);
    }
    bcm2835_gpio_write(pinning[active_pinning].oe_white, 0);
    while(bcm2835_gpio_lev(pinning[active_pinning].oe_white)){
        bcm2835_gpio_write(pinning[active_pinning].oe_white, 0);
    }
}
