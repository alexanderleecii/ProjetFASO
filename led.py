import grovepi as gp
import time
led=4
gp.pinMode(led, "OUTPUT")
while True :
	try:
		gp.digitalWrite(led,1)

	except IOError:
		print("Error")
