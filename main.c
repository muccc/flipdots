#ifndef F_CPU
#define F_CPU 16000000
#endif

#include <avr/io.h>
#include <util/delay.h>

#define DATA_COL (1<<PC6) //output 7
#define DATA_ROW (1<<PC0) //output 1
#define STROBE   (1<<PC1) //output 2

#define OE_WHITE (1<<PC3) //output 3
#define OE_BLACK (1<<PC2) //output 4

#define CLK_COL  (1<<PC4) //output 5
#define CLK_ROW  (1<<PC5) //output 6

#define CLK_DELAY  3			/* us */
#define FLIP_DELAY 5			/* ms */
#define STROBE_DELAY 3			/* us */

#define DISP_COLS   16
#define DISP_ROWS   24

enum sreg {
	ROW,
	COL
};

#define DATA(reg)								\
	((reg == ROW) ? DATA_ROW : DATA_COL)
#define CLK(reg)								\
	((reg == ROW) ? CLK_ROW : CLK_COL)
#define OE(reg)									\
	((reg == ROW) ? OE_ROW : OE_COL)

void sreg_push_bit(enum sreg reg, uint8_t bit);
void sreg_fill(enum sreg reg, int count, uint64_t data);

void strobe(void);
void flip_pixels(void);

int main( void ) {
	// init ports
	DDRC  |=  (DATA_COL|STROBE|OE_WHITE|OE_BLACK|CLK_ROW|CLK_COL|DATA_ROW);
	PORTC &= ~(DATA_COL|STROBE|OE_WHITE|OE_BLACK|CLK_ROW|CLK_COL|DATA_ROW);

	for (int col = 0; col < DISP_COLS; ++col) {
		/* Checkerboard */
		uint64_t row_data = (col%2 == 0) ? 0x55555 : 0xaaaaa;
		
		sreg_push_bit(COL, 1);
		for (int row = 0; row < DISP_ROWS; ++row) {
			PORTC &= ~(OE_WHITE);
			PORTC &= ~(OE_BLACK);

            // let's play safe
			PORTC &= ~(STROBE);
			PORTC &= ~(DATA_COL);
			PORTC &= ~(DATA_ROW);
			PORTC &= ~(CLK_COL);
			PORTC &= ~(CLK_ROW);

			sreg_fill(ROW, DISP_ROWS, row_data);
			strobe();
			flip_pixels();

			sreg_push_bit(COL, 0);
		}

		_delay_ms(1000);
	}

	return 0;
}

/* Output bit on reg and pulse clk signal */
void sreg_push_bit(enum sreg reg, uint8_t bit) {
	PORTC |= DATA(reg);			/* set data bit */
	
	PORTC |= CLK(reg); 			/* clk high */
	_delay_us(CLK_DELAY);		/* Wait */
	PORTC &= CLK(reg);			/* clk low */
}

/* Fill register reg with count bits from data LSB first */
void sreg_fill(enum sreg reg, int count, uint64_t data) {
	for (int i; i < count; ++i) {
		uint8_t bit = data & 1;
		sreg_push_bit(reg, bit);
		data >>= 1;
	}
}

void strobe(void) {
	PORTC |= STROBE;
	_delay_us(STROBE_DELAY);
}

void flip_pixels(void) {
	// set white pixels
	PORTC |= (OE_WHITE);
	PORTC &= ~(OE_BLACK);
	_delay_ms( FLIP_DELAY );

	// set black pixels
	PORTC |= (OE_BLACK);
	PORTC &= ~(OE_WHITE);
	
	_delay_ms( FLIP_DELAY );
}
