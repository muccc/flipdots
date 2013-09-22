#include <unistd.h>
#include <stdint.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <linux/spi/spidev.h>
#include <stdio.h>
#include <errno.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

static uint8_t mode;
static uint8_t bitsPerWord;
static int speed;
int spifd;

static int simplespi_open(char *devspi)
{
	int statusVal = -1;
	spifd = open(devspi, O_RDWR);
	if(spifd < 0){
		perror("could not open SPI device");
		exit(1);
	}

	statusVal = ioctl (spifd, SPI_IOC_WR_MODE, &(mode));
	if(statusVal < 0){
		perror("Could not set SPIMode (WR)...ioctl fail");
		exit(1);
	}

	statusVal = ioctl (spifd, SPI_IOC_RD_MODE, &(mode)); 
	if(statusVal < 0) {
	  perror("Could not set SPIMode (RD)...ioctl fail");
	  exit(1);
	}

	statusVal = ioctl (spifd, SPI_IOC_WR_BITS_PER_WORD, &(bitsPerWord));
	if(statusVal < 0) {
	  perror("Could not set SPI bitsPerWord (WR)...ioctl fail");
	  exit(1);
	}

	statusVal = ioctl (spifd, SPI_IOC_RD_BITS_PER_WORD, &(bitsPerWord));
	if(statusVal < 0) {
	  perror("Could not set SPI bitsPerWord(RD)...ioctl fail");
	  exit(1);
	} 	

	statusVal = ioctl (spifd, SPI_IOC_WR_MAX_SPEED_HZ, &(speed)); 	
	if(statusVal < 0) {
	  perror("Could not set SPI speed (WR)...ioctl fail");
	  exit(1);
	} 

	statusVal = ioctl (spifd, SPI_IOC_RD_MAX_SPEED_HZ, &(speed)); 	
	if(statusVal < 0) {
	  perror("Could not set SPI speed (RD)...ioctl fail");
	  exit(1);
	}
	return statusVal;
}

/***********************************************************
 * spiClose(): Responsible for closing the spidev interface.
 * Called in destructor
 * *********************************************************/

int simplespi_close()
{
	int statusVal = -1;
	statusVal = close(spifd);
    	if(statusVal < 0) {
	  perror("Could not close SPI device");
	  exit(1);
	}
	return statusVal;
}

/********************************************************************
 * This function writes data "data" of length "length" to the spidev
 * device. Data shifted in from the spidev device is saved back into 
 * "data". 
 * ******************************************************************/
int simplespi_write_read(uint8_t *data, int length, bool do_rx)
{
    struct spi_ioc_transfer transfer[1];
    int retVal = -1; 

    transfer[0].tx_buf = (unsigned long)data; // transmit from "data"
    if(do_rx){
        transfer[0].rx_buf = (unsigned long)data; // receive into "data"
    }else{
        transfer[0].rx_buf = (unsigned long)NULL; // do not receive
    }

    transfer[0].len           = length;
    transfer[0].delay_usecs   = 0 ; 
    transfer[0].speed_hz      = speed;
    transfer[0].bits_per_word = bitsPerWord;
    transfer[0].cs_change = 0;
    transfer[0].delay_usecs = 0;

    retVal = ioctl(spifd, SPI_IOC_MESSAGE(1), &transfer);

    if(retVal < 0){
        perror("Problem transmitting spi data..ioctl");
        exit(1);
    }

    return retVal;
}

int simplespi_write_read_list(uint8_t *data, int n, int length, bool do_rx)
{
    struct spi_ioc_transfer transfer[n];
    int i;
    int retVal = -1; 
    for(i=0; i<n; i++){
        transfer[i].tx_buf = ((unsigned long)data) + i * length; // transmit from "data"
        if(do_rx){
            transfer[i].rx_buf = ((unsigned long)data) + i * length; // receive into "data"
        }else{
            transfer[i].rx_buf = (unsigned long)NULL; // do not receive
        }
        transfer[i].len           = length;
        transfer[i].delay_usecs   = 0 ; 
        transfer[i].speed_hz      = speed;
        transfer[i].bits_per_word = bitsPerWord;
        transfer[i].cs_change = 1;
        transfer[i].delay_usecs = 0;
    }

    retVal = ioctl(spifd, SPI_IOC_MESSAGE(n), &transfer);

    if(retVal < 0){
        perror("Problem transmitting spi data..ioctl");
        exit(1);
    }

    return retVal;
}
/*************************************************
 * Default constructor. Set member variables to
 * default values and then call spiOpen()
 * ***********************************************/

int simplespi_init(void)
{
    mode = SPI_MODE_0;
    bitsPerWord = 8;
    speed = 20000000;
    spifd = -1;

    return simplespi_open("/dev/spidev0.0");
}

