#!/usr/bin/env python3
from FlipdotAPI.FlipdotMatrix import FlipdotMatrix, FlipdotImage
import argparse
import qrcode


class QR:
	
	def __init__(self, text):
		self.matrix = FlipdotMatrix(imageSize=(144,120))
		self.text = text



	def __generateQrImage(self):
		self.qr = qrcode.QRCode(
    		version=1,
    		error_correction=qrcode.constants.ERROR_CORRECT_H,
    		box_size=40,
    		border=4,
		)
		self.qr.add_data(self.text)
		self.qr.make(fit=True)
		
		self.img = qr.make_image(fill_color="black", back_color="white")


	
	def sendToPanel(self):
		//todo
	
	
	


if __name__=='__main__':
	parser = argparse.ArgumentParser(description='send a qr code to the flipdot')
    parser.add_argument('text', help='text/url to send as qr-code')
 	args = parser.parse_args()
 	
    
	qr = QR(args.text)
	qr.sendToPanel()
