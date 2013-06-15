#ifndef F_CPU
#define F_CPU 16000000
#endif
// Hey Fucker, this is still work/hack in progress, don't expect anything usefull here!
#include <avr/io.h>
#include <util/delay.h>
//#include <avr/interrupt.h>


#define DATA_COL (1<<PC6) //output 7
#define DATA_ROW (1<<PC0) //output 1
#define STROBE   (1<<PC1) //output 2
//#define OE_WHITE (1<<PC2) //output 3
//#define OE_BLACK (1<<PC3) //output 4

#define OE_WHITE (1<<PC3) //output 3
#define OE_BLACK (1<<PC2) //output 4

#define CLK_COL  (1<<PC4) //output 5
#define CLK_ROW  (1<<PC5) //output 6


#define CLK_DELAY  3  /* us */
#define FLIP_DELAY 5 /* ms */

#define DISP_COLS   16
#define DISP_ROWS   24


void write_col( uint8_t colIndex, uint64_t data );



int main( void ) {
	uint32_t data;
	uint8_t  row=0, col=1;

	// init ports
	DDRC  |=  (DATA_COL|STROBE|OE_WHITE|OE_BLACK|CLK_ROW|CLK_COL|DATA_ROW);
	PORTC &= ~(DATA_COL|STROBE|OE_WHITE|OE_BLACK|CLK_ROW|CLK_COL|DATA_ROW);


	uint64_t mask = 1, i =0, j=0;

  
	for( row=0; row<DISP_COLS; row++ ) {
		write_col( row, 0);
		_delay_ms(2);
	}
	_delay_ms(1000);


	while( 1 ) {
		if ( i%DISP_ROWS == 0 ) mask = 1;
		for( row=0; row<DISP_COLS; row++ ) {
			//if ( i%24 < 4 ) continue;	
			data |= ((uint64_t)mask<<row);

			write_col( row, ((row+i)%2) ? 0b1010101010101010101010101 : 0b0101010101010101010101010 ); // 1x1 schachbrett
			//write_col( row, ((uint64_t)mask<<row) );
			//write_col( row, j+=16);
			//write_col( row, mask);
			//write_col( row-1, 0);


			_delay_ms(10); // for sanity
			
		}
		mask=mask<<1;
		i++;
		//if (col < DISP_COLS-1) {
		//	col++;
		//} else {
		//	col = 0;
		//}
	}
	return 0;
}



void write_col( uint8_t colIndex, uint64_t data ) {
	uint8_t i;
	uint8_t _colCurIndex=0;
	uint8_t _pixelDat=0;
	uint8_t _pixelCurIndex=0;

	// TODO: mask data

	// all drivers off
	PORTC &= ~(OE_WHITE);
	PORTC &= ~(OE_BLACK);

	// let's play save
	PORTC &= ~(STROBE);
	PORTC &= ~(DATA_COL);
	PORTC &= ~(DATA_ROW);
	PORTC &= ~(CLK_COL);
	PORTC &= ~(CLK_ROW);

	// select col
	for( _colCurIndex=0; _colCurIndex < DISP_COLS; _colCurIndex++) {
		// one extra clock to push out a "don't care"
		// because it loses a bit at the transfer to the next section
		if( _colCurIndex == colIndex ) {
			PORTC |= (DATA_COL);
		}
		else {
			PORTC &= ~(DATA_COL);
		}
		_delay_us( CLK_DELAY );

		PORTC |= (CLK_COL);
		_delay_us( CLK_DELAY );
		PORTC &= ~(CLK_COL);
	}


	// write data for each row in that col
	for( _pixelCurIndex=0; _pixelCurIndex<(DISP_ROWS); _pixelCurIndex++ ) {
//		if(_pixelCurIndex<16){
			_pixelDat = data & ((uint64_t)1 << _pixelCurIndex) ? 1: 0;
//		}else{
//			_pixelDat = data&(1<<_pixelCurIndex)? 0: 1;
//		}
		if( _pixelDat ) {
			PORTC &= ~(DATA_ROW);
		}
		else {
			PORTC |= (DATA_ROW);
		}
		_delay_us( CLK_DELAY );

		PORTC |= (CLK_ROW);
		_delay_us(CLK_DELAY);

		PORTC &= ~(CLK_ROW);
	}

	// commit data
	PORTC |= STROBE;

	// set whities
	PORTC |= (OE_WHITE);
	PORTC &= ~(OE_BLACK);
	_delay_ms( FLIP_DELAY );

	// set blackies
	PORTC |= (OE_BLACK);
	PORTC &= ~(OE_WHITE);
	
	_delay_ms( FLIP_DELAY );


	// all drivers off
//	PORTD &= ~(OE_WHITE);
//	PORTD &= ~(OE_BLACK);
}

