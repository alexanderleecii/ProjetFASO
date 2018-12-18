# coding: utf-8

from driverI2C import *
import grovepi
import time
from Projet import *
import os

def Est_Bouteille_Posee():
	if grovepi.ultrasonicRead(ultrason)<8:
		return True
	else:
		return False

def Est_Bouteille_Posee_3():
	tmp_debut=time.time()
	tmp_fin=time.time()
	while tmp_fin-tmp_debut<3:
		tmp_fin=time.time()
		if not Est_Bouteille_Posee():
			return False
	return True
	
#faire cette fonction	
def Get_Temperature():
	return 6.5
	
#faire cette fonction	
def Est_Bouteille_Fraiche(Temps):
	a=Temps	
	return False

def Choisir_Bouteille():
	while True:
		if grovepi.digitalRead(button1)==1:
			return 3
		if grovepi.digitalRead(button2)==1:
			return 7
	
def Init():
	if not Est_Bouteille_Posee():
		setText(" Poser la bouteille")
		return 0
	else:
		if not Est_Bouteille_Posee_3():
			return 0
		else:
			setText(" Choisir bouteille")
			tmp=Choisir_Bouteille()
			return tmp
			
def Actionner(Temps):
	tmp_debut=time.time()
	tmp_fin=time.time()
	while tmp_fin-tmp_debut<Temps:
		if not Est_Bouteille_Posee():
			return 0
		else:
			grovepi.digitalWrite(relay,1)
			grovepi.digitalWrite(relayDC,1)
			setText(" Decapsulage en cours")
			tmp_fin=time.time()
	grovepi.digitalWrite(relay,0)
	return 1

def Retracter(Temps):
	grovepi.digitalWrite(relay,1)
	grovepi.digitalWrite(relayDC,0)
	time.sleep(Temps)
	grovepi.digitalWrite(relay,0)
	
def Decapsulage_Force():
	while True:
		if grovepi.digitalRead(button1)==1:
			return True
		if grovepi.digitalRead(button2)==1:
			return False

def TestTemperature(Temps):
	if not Est_Bouteille_Fraiche(Temps):
		temperature=Get_Temperature()		
		setText(" " + str(temperature))
		time.sleep(1.5)
		setText(" Bouteille pas assez fraiche")
		time.sleep(1.5)
		setText(" Quand meme decapsuler ?")
		if not Decapsulage_Force():
			return 0
	else:
		temperature=Get_Temperature()	
		setText(" " + str(temperature))
		time.sleep(1.5)
		setText(" Bouteille fraiche")
		time.sleep(1.5)
	if not Est_Bouteille_Posee():
		return 0
	else:
		return 1
		
def buzzer_fin():
	grovepi.digitalWrite(buzzer,1)
	time.sleep(.5)
	grovepi.digitalWrite(buzzer,0)
	time.sleep(.5)
	grovepi.digitalWrite(buzzer,1)
	time.sleep(.5)
	grovepi.digitalWrite(buzzer,0)

relay = 2
button1 = 3
button2 = 5
ultrason = 4
buzzer = 6
relayDC = 7
grovepi.pinMode(button1,"INPUT")
grovepi.pinMode(button2,"INPUT")
grovepi.pinMode(relay,"OUTPUT")
grovepi.pinMode(relayDC,"OUTPUT")
Temps=0

os.system("sudo /home/ig3/ProjetFas/./Projet.sh")

while True:
	try:
		if Temps==0:
			Temps=Init()
			continue
		if TestTemperature(Temps)==0:
			Temps=0
			continue
		if Actionner(Temps)==0:
			setText(" Interruption Decapsulage")
			grovepi.digitalWrite(relay,0)		
			time.sleep(2)
			Retracter(Temps)
			Temps=0
			continue	
		time.sleep(2)
		Retracter(Temps)
		buzzer_fin()
		#Rajouter les stats
		setText(" Decapsulage termine")
		Temps=0
	
	except KeyboardInterrupt:
		grovepi.digitalWrite(relay,0)
		grovepi.digitalWrite(relayDC,0)
		grovepi.digitalWrite(buzzer,0)
		break
	except TypeError:
		print "Error1"
		grovepi.digitalWrite(relay,0)
		grovepi.digitalWrite(relayDC,0)
		grovepi.digitalWrite(buzzer,0)
	except IOError:
		print "Error2"
		grovepi.digitalWrite(relay,0)
		grovepi.digitalWrite(relayDC,0)
		grovepi.digitalWrite(buzzer,0)		
		
		
		
