# coding: utf-8

from driverI2C import *
import time
from Projet import *
import grovepi
from grovepi import *
import os

relay = 2
button = 3
ultrason = 4
buzzer = 6
relayDC = 7
temps=-1
grovepi.pinMode(button,"INPUT")
grovepi.pinMode(relay,"OUTPUT")
grovepi.pinMode(relayDC,"OUTPUT")
testbouton=0
os.system("sudo /home/ig3/ProjetFas/./Projet.sh")
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
					try:
						if grovepi.digitalRead(button):
							setText(" Et merce")
							grovepi.digitalWrite(relay,1)
							grovepi.digitalWrite(relayDC,1)
							print ("Actionner")
							time.sleep(3)
							grovepi.digitalWrite(relay,0)
							time.sleep(1)
							grovepi.digitalWrite(relay,1)
							grovepi.digitalWrite(relayDC,0)
							print ("Retracter")
							time.sleep(3)
						else:
							grovepi.digitalWrite(relay,0)
							time.sleep(.05)
						testbouton=1
						time.sleep(1)
						grovepi.digitalWrite(buzzer,1)
						time.sleep(.5)
						grovepi.digitalWrite(buzzer,0)
						time.sleep(.5)
						grovepi.digitalWrite(buzzer,1)
						time.sleep(.5)
						grovepi.digitalWrite(buzzer,0)
						time.sleep(2)
					except KeyboardInterrupt:
						grovepi.digitalWrite(relay,0)
						grovepi.digitalWrite(relayDC,0)
						grovepi.digitalWrite(buzzer,0)
    					break
	except TypeError:
		print "Error"
	except IOError:
		print "Error"
