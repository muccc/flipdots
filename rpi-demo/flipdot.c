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

#include <max7301.h>
#include <stdint.h>
#include <string.h>
#include <stdbool.h>
#include <unistd.h>

extern int usleep (__useconds_t __useconds);
#define _delay_us(x) usleep(x)


#define ISBITSET(x,i) ((x[i>>3] & (1<<(i&7)))!=0)
#define SETBIT(x,i) x[i>>3]|=(1<<(i&7));
#define CLEARBIT(x,i) x[i>>3]&=(1<<(i&7))^0xFF;

#define DATA(reg)								\
	((reg == ROW) ? DATA_ROW : DATA_COL)
#define CLK(reg)								\
	((reg == ROW) ? CLK_ROW : CLK_COL)
#define OE(reg)									\
	((reg == ROW) ? OE_ROW : OE_COL)

#define LEN(a)									\
	(sizeof(a)/sizeof(a[0]))

static uint8_t buffer_a[DISP_BYTE_COUNT];
static uint8_t buffer_b[DISP_BYTE_COUNT];
static uint8_t buffer_to_0[DISP_BYTE_COUNT];
static uint8_t buffer_to_1[DISP_BYTE_COUNT];
static uint8_t *buffer_new, *buffer_old;

static void sreg_push_bit(enum sreg reg, uint8_t bit);
static void sreg_fill(enum sreg reg, uint8_t *data, int count);
static void sreg_fill_row(uint8_t *data, int count);
static void sreg_fill_col(uint8_t *data, int count);

static void strobe(void);
static void flip_white(void);
static void flip_black(void);

uint8_t diff_to_0(uint8_t old, uint8_t new);
uint8_t diff_to_1(uint8_t old, uint8_t new);

static void map_two_buffers(uint8_t (*fun)(uint8_t, uint8_t), uint8_t a[], uint8_t b[], uint8_t dst[], unsigned int count);

static void display_frame_differential(uint8_t *to_0, uint8_t *to_1);

void
flipdot_init(void)
{
    max7301_init(100, false);

	/* init pins */
    max7301_set_pin_as_output(DATA_COL);
    max7301_set_pin_as_output(DATA_ROW);
    max7301_set_pin_as_output(STROBE);
    max7301_set_pin_as_output(OE_WHITE);
    max7301_set_pin_as_output(OE_BLACK);
    max7301_set_pin_as_output(CLK_COL);
    max7301_set_pin_as_output(CLK_ROW);

	/* Init buffer pointers */
	buffer_new = buffer_a;
	buffer_old = buffer_b;

	/* Synchronize buffers and flipdot pixel state */
	memset(buffer_new, 0xFF, DISP_BYTE_COUNT);
	memset(buffer_old, 0x00, DISP_BYTE_COUNT);
	flipdot_data(buffer_old, DISP_BYTE_COUNT);
	flipdot_data(buffer_old, DISP_BYTE_COUNT);
	flipdot_data(buffer_old, DISP_BYTE_COUNT);
}

void
flipdot_data(uint8_t *frame, uint16_t size)
{
	uint8_t *tmp;
	
	memcpy(buffer_old, frame, size); /* Copy frame into buffer with old data */

	tmp = buffer_old;				 /* swap pointers buffer_new and buffer_old */
	buffer_old = buffer_new;
	buffer_new = tmp;
	
	map_two_buffers(diff_to_0, buffer_old, buffer_new, buffer_to_0, DISP_BYTE_COUNT);
	map_two_buffers(diff_to_1, buffer_old, buffer_new, buffer_to_1, DISP_BYTE_COUNT);

	display_frame_differential(buffer_to_0, buffer_to_1);
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
		
		sreg_fill(ROW, row_data_to_0, REGISTER_COLS); /* Fill row to 0 shift register */
		strobe();
	    flip_black();

		sreg_fill(ROW, row_data_to_1, REGISTER_COLS); /* Fill row to 1 shift register */
		strobe();
		flip_white();
	}
}

/* Output bit on reg and pulse clk signal */
static void
sreg_push_bit(enum sreg reg, uint8_t bit)
{
    max7301_set_pin(DATA(reg), bit);
    max7301_step();
    max7301_set_pin(CLK(reg), 1);
    max7301_step();
	//_delay_us(CLK_DELAY);		/* Wait */
    max7301_set_pin(CLK(reg), 0);
    max7301_step();
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
	count -= ROW_GAP;
	int i = 0;
	int halt_count = 0;
	while (i < count) {
		if (i > MODULE_COLS && halt_count < ROW_GAP) {
			++halt_count;
			--i;
		}
		/* count-i-1 because the first bit needs to go last */
		sreg_push_bit(ROW, ISBITSET(data, (count-i-1)));
		++i;
	}
}

static void
strobe(void)
{
    max7301_set_pin(STROBE, 1);
    //max7301_step();
    max7301_flush_history();
	_delay_us(STROBE_DELAY);
    max7301_set_pin(STROBE, 0);
    //max7301_step();
    max7301_flush_history();
}

static void
flip_white(void)
{
    max7301_flush_history();
    max7301_set_pin(OE_BLACK, 0);
    max7301_set_pin(OE_WHITE, 1);
    max7301_step();
    max7301_flush_history();

	_delay_us(FLIP_DELAY);

    max7301_set_pin(OE_BLACK, 0);
    max7301_set_pin(OE_WHITE, 0);
    max7301_step();
    max7301_flush_history();
}

static void
flip_black(void)
{
    max7301_flush_history();
    max7301_set_pin(OE_BLACK, 1);
    max7301_set_pin(OE_WHITE, 0);
    max7301_step();
    max7301_flush_history();

	_delay_us(FLIP_DELAY);

    max7301_set_pin(OE_BLACK, 0);
    max7301_set_pin(OE_WHITE, 0);
    max7301_step();
    max7301_flush_history();
}
