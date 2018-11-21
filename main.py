# coding: utf-8

from driverI2C import *
import time
from Projet import *
import grovepi
from grovepi import *

ultrason = 4
button = 3
temps=-1
grovepi.pinMode(button,"INPUT")
testbouton=0
while temps==-1:
	try:
		if(ultrasonicRead(ultrason))<8:
			while(ultrasonicRead(ultrason)<8 and temps<=3):
				time.sleep(1)
				temps=temps+1
			if temps>3:
				temps=-1
				setText(" Veuillez choisir un type de bouteille")
				while testbouton==0:
					if grovepi.digitalRead(button):
						setText(" Et merce")
						testbouton=1
						time.sleep(5)
	except TypeError:
		print "Error"
	except IOError:
		print "Error"
