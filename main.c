#define F_CPU 16000000
// Hey Fucker, this is still work/hack in progress, don't expect anything usefull here!
#include <avr/io.h>
#include <util/delay.h>
#include <avr/interrupt.h>


#define DATA_COL (1<<PB0)
#define DATA_ROW (1<<PD2)
#define STROBE   (1<<PD3)
#define OE_WHITE (1<<PD4)
#define OE_BLACK (1<<PD5)
#define CLK_COL  (1<<PD6)
#define CLK_ROW  (1<<PD7)


#define CLK_DELAY 5  /* us */
#define FLIP_DELAY 5 /* ms */

#define DISP_COLS 16
#define DISP_ROWS 20



int8_t write_col( uint8_t colIndex, uint32_t data );



int main( void ) {
	uint32_t data;
	uint8_t  row=0, col=0;

	// init ports
	DDRD  |=  (DATA_COL|STROBE|OE_WHITE|OE_BLACK|CLK_ROW|CLK_COL);
	PORTD &= ~(DATA_COL|STROBE|OE_WHITE|OE_BLACK|CLK_ROW|CLK_COL);

	DDRB  |=  (DATA_ROW);
	PORTB &= ~(DATA_ROW);

	while( 1 ) {
		for( row=0; row<DISP_ROWS; row++ ) {
			data = ((uint32_t)1<<row);

			// write a single screen
			for( col=0; col< DISP_COLS; col++ ) {
				write_col( col, data );
			}

			_delay_ms(500); // for sanity
		}
	}
}



int8_t write_col( uint8_t colIndex, uint32_t data ) {
	uint8_t i;
	uint8_t _colCurIndex=0;
	uint8_t _pixelDat=0;
	uint8_t _pixelCurIndex=0;

	// TODO: mask data

	// all drivers off
	PORTD &= ~(OE_WHITE);
	PORTD &= ~(OE_BLACK);

	// let's play save
	PORTD &= ~(STROBE);
	PORTB &= ~(DATA_COL);
	PORTD &= ~(DATA_ROW);
	PORTD &= ~(CLK_COL);
	PORTD &= ~(CLK_ROW);

	// select col
	for( _colCurIndex=0; _colCurIndex < DISP_COLS; _colCurIndex++) {
		// one extra clock to push out a "don't care"
		// because it loses a bit at the transfer to the next section
		if( _colCurIndex == colIndex ) {
			PORTB |= (DATA_COL);
		}
		else {
			PORTB &= ~(DATA_COL);
		}
		_delay_us( CLK_DELAY );

		PORTD |= (CLK_COL);
		_delay_us( CLK_DELAY );
		PORTD &= ~(CLK_COL);
	}


	// write data for each row in that col
	for( _pixelCurIndex=0; _pixelCurIndex<(DISP_ROWS); _pixelCurIndex++ ) {
//		if(_pixelCurIndex<16){
			_pixelDat = data&((uint32_t)1<<_pixelCurIndex)? 1: 0;
//		}else{
//			_pixelDat = data&(1<<_pixelCurIndex)? 0: 1;
//		}
		if( _pixelDat ) {
			PORTD &= ~(DATA_ROW);
		}
		else {
			PORTD |= (DATA_ROW);
		}
		_delay_us( CLK_DELAY );

		PORTD |= (CLK_ROW);
		_delay_us(CLK_DELAY);

		PORTD &= ~(CLK_ROW);
	}

	// commit data
	PORTD |= STROBE;

	// set whities
	PORTD |= (OE_WHITE);
	PORTD &= ~(OE_BLACK);
	_delay_ms( FLIP_DELAY );

	// set blackies
	PORTD &= ~(OE_WHITE);
	PORTD |= (OE_BLACK);
	_delay_ms( FLIP_DELAY );


	// all drivers off
//	PORTD &= ~(OE_WHITE);
//	PORTD &= ~(OE_BLACK);
}

