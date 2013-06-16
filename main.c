#ifndef F_CPU
#define F_CPU 16000000
#endif

#include <avr/io.h>
#include <util/delay.h>

#define DATA_COL (1<<PC6) //output 7
#define DATA_ROW (1<<PC0) //output 1
#define STROBE   (1<<PC1) //output 2

#define OE_WHITE (1<<PC3) //output 4
#define OE_BLACK (1<<PC2) //output 3

#define CLK_COL  (1<<PC4) //output 5
#define CLK_ROW  (1<<PC5) //output 6

#define CLK_DELAY  1			/* us */
#define FLIP_DELAY 1			/* ms */
#define STROBE_DELAY 1			/* us */
#define LINE_DELAY 0			/* ms */

#define DISP_COLS   24 + 20
#define DISP_ROWS   16

#define FRAME_DELAY 0

enum sreg {
	ROW,
	COL
};

#define ISBITSET(x,i) ((x[i>>3] & (1<<(i&7)))!=0)
#define SETBIT(x,i) x[i>>3]|=(1<<(i&7));
#define CLEARBIT(x,i) x[i>>3]&=(1<<(i&7))^0xFF;

#define DATA(reg)								\
	((reg == ROW) ? DATA_ROW : DATA_COL)
#define CLK(reg)								\
	((reg == ROW) ? CLK_ROW : CLK_COL)
#define OE(reg)									\
	((reg == ROW) ? OE_ROW : OE_COL)

void sreg_push_bit(enum sreg reg, uint8_t bit);
void sreg_fill(enum sreg reg, int count, uint8_t *data);

void strobe(void);
void flip_pixels(void);

void display_frame(uint8_t *row_data);

#include "frame1.xbm"
#include "frame2.xbm"
#include "frame3.xbm"
#include "frame4.xbm"
#include "frame5.xbm"
#include "frame6.xbm"
#include "frame7.xbm"
#include "frame8.xbm"
#include "frame9.xbm"
#include "frame10.xbm"
#include "frame11.xbm"
#include "frame12.xbm"

#define FRAMES(X)									\
	X(frame1),										\
	X(frame2),										\
	X(frame3),										\
	X(frame4),										\
	X(frame5),										\
	X(frame6),										\
	X(frame7),										\
	X(frame8),										\
	X(frame9),										\
	X(frame10),										\
	X(frame11),										\
	X(frame12)

#define AS_BITS(f)								\
	f##_bits

uint8_t white[5*16] = {0x00};
uint8_t black[5*16] = {0x00};

uint8_t *frames[] = {
	FRAMES(AS_BITS),
	frame11_bits,
	frame10_bits,
	frame9_bits,
	frame8_bits,
	frame7_bits,
	frame6_bits,
	frame5_bits,
	frame4_bits,
	frame3_bits,
	frame2_bits
};

int main( void ) {
	// init ports
	DDRC  |=  (DATA_COL|STROBE|OE_WHITE|OE_BLACK|CLK_ROW|CLK_COL|DATA_ROW);
	PORTC &= ~(DATA_COL|STROBE|OE_WHITE|OE_BLACK|CLK_ROW|CLK_COL|DATA_ROW);

	for (int i = 0; i < 5*16; ++i) {
		white[i] = 0x00;
		black[i] = 0xFF;
	}
	
	for (int i = 0;; ++i) {
		display_frame(frames[i% sizeof(frames)/sizeof(frames[0])]);
	}

	return 0;
}

void write_bit(uint8_t *byte, int pos, uint8_t bit) {
	*(byte + pos/8) |= (bit << pos%8);
}

void display_frame(uint8_t *data) {
	uint8_t row_select[DISP_ROWS/8];
	
	for (int row = 0; row < DISP_ROWS; ++row) { /* Every row */
		uint8_t *row_data = data + row * (DISP_COLS-4)/8; /* -4 should be +4 above */

		for (int i = 0; i < DISP_ROWS/8; ++i) { /* Clear row_select */
			row_select[i] = 0;
		}
		SETBIT(row_select, row); /* Set selected row */
		sreg_fill(COL, DISP_ROWS, row_select); /* Fill row select shift register */
		
		sreg_fill(ROW, DISP_COLS, row_data); /* Fill row data shift register */
		strobe();
		flip_pixels();

		/* _delay_ms(LINE_DELAY); */
	}
}

/* Output bit on reg and pulse clk signal */
void sreg_push_bit(enum sreg reg, uint8_t bit) {
	if (bit) {
		PORTC |= DATA(reg);			/* set data bit */
	} else {
		PORTC &= ~DATA(reg);			/* unset data bit */
	}
	
	PORTC |= CLK(reg); 			/* clk high */
	_delay_us(CLK_DELAY);		/* Wait */
	PORTC &= ~CLK(reg);			/* clk low */
}

/* Fill register reg with count bits from data LSB first */
void sreg_fill(enum sreg reg, int count, uint8_t *data) {
	if (reg == ROW) {
		count -= 4;
	}
	int i = 0;
	int halt_count = 0;
	while (i < count) {
		if (reg == ROW) {
			if (i > 20 && halt_count < 4) {
				++halt_count;
				--i;
			}
		}
		sreg_push_bit(reg, ISBITSET(data, i));
		++i;
	}
}

void strobe(void) {
	PORTC |= STROBE;
	_delay_us(STROBE_DELAY);
	PORTC &= ~STROBE;
}

void flip_pixels(void) {
	// set white pixels
	PORTC |= (OE_WHITE);
	PORTC &= ~(OE_BLACK);

	_delay_ms(FLIP_DELAY);

	// set black pixels
	PORTC |= (OE_BLACK);
	PORTC &= ~(OE_WHITE);
	
	_delay_ms(FLIP_DELAY);

	PORTC &= ~(OE_BLACK);
	PORTC &= ~(OE_WHITE);
}
