# coding: utf-8

import time
import grovepi
from grovepi import *

relay = 4
button = 3
relayDC = 7
test=1
grovepi.pinMode(button,"INPUT")
grovepi.pinMode(relay,"OUTPUT")
grovepi.pinMode(relayDC,"OUTPUT")

while True:
    try:
		if digitalRead(button):
			grovepi.digitalWrite(relay,1)
			grovepi.digitalWrite(relayDC,1)
			print ("Actionner")
			time.sleep(3)
			grovepi.digitalWrite(relayDC,0)
			print ("Actionner")
			time.sleep(3)
		else:
			grovepi.digitalWrite(relay,0)
			time.sleep(.05)

    except KeyboardInterrupt:
        grovepi.digitalWrite(relay,0)
		grovepi.digitalWrite(relayDC,0)
        break
    except IOError:
        print ("Error")
