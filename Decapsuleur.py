# coding: utf-8
from __future__ import print_function
from driverI2C import *
import grovepi2
import grovepi
import time
from Projet import *
import sys, signal, atexit
from upm import pyupm_otp538u as upmOtp538u
import mraa
import os
import requests
import urllib3
from decimal import Decimal
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name('FASOconnexiongoogle.json',scope)

gc = gspread.authorize(credentials)

wks1 = gc.open("Temperature 1").sheet1
wks2 = gc.open("Temperature 2").sheet1

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def setOff():
	tmp_debut=time.time()
	tmp_fin=time.time()
	while tmp_fin-tmp_debut<2:
		tmp_fin=time.time()
		if grovepi.digitalRead(button1)==0 or grovepi.digitalRead(button2)==0:
			return False
	return True

def nb_decap():
	nb1=int(wks1.cell(3,5).value)
	nb2=int(wks2.cell(3,5).value)
	return nb1+nb2

def envoi_temp(temperature,num):
	if (num == 1):
		requests.post('https://docs.google.com/forms/d/1KQa6qJuVxa7fWpZ3pcpd1S1MyM2B2OyjpYDz9uVt5w0/formResponse', data = {'entry.824402807':temperature},verify=False)
	if (num == 2):
		requests.post('https://docs.google.com/forms/d/1CV02WCQ15aaTsvUOA22GWnhpHbgEmU5XQaAGf3uDKew/formResponse', data = {'entry.1298687124':temperature},verify=False)
	if (num!=1 and num!=2):
		print("error")
		
def recevoir_temp_moyenne(Temps): 
	if (Temps == 3):
		temperature_ideale=wks1.cell(4,4).value
	if (Temps == 7):
		temperature_ideale=wks2.cell(4,4).value
	if (Temps!=3 and Temps!=7):
		print("error")
		return -1
	return temperature_ideale
	
def Est_Bouteille_Posee():
	if grovepi2.ultrasonicRead(ultrason)<8:
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
    	# Register exit handlers
    	#atexit.register(exitHandler)
    	#signal.signal(signal.SIGINT, SIGINTHandler)

        return(round(float(myTempIR.objectTemperature()),2))
	
#faire cette fonction	
def Est_Bouteille_Fraiche(Temps):
	temperature_ideale=float(recevoir_temp_moyenne(Temps).replace(',','.'))
	temperature_bouteille=Get_Temperature()
	if (temperature_bouteille<temperature_ideale) :
		return True
	else:
		return False

def Choisir_Bouteille():
	while True:
		if grovepi.digitalRead(button1)==1:
			return 3
		if grovepi.digitalRead(button2)==1:
			return 7
	
def Init():
	if setOff():
		return -1
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
		if grovepi2.digitalRead(button1)==1:
			return True
		if grovepi2.digitalRead(button2)==1:
			return False

def TestTemperature(Temps):
	if not Est_Bouteille_Fraiche(Temps):
		temperature=Get_Temperature()		
		setText(" Temperature : " + str(temperature)+" C")
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
grovepi2.pinMode(button1,"INPUT")
grovepi2.pinMode(button2,"INPUT")
grovepi.pinMode(relay,"OUTPUT")
grovepi.pinMode(relayDC,"OUTPUT")
Temps=0

mraa.addSubplatform(mraa.GROVEPI, "0")
OTP538U_AREF = 5.0 # analog voltage, usually 3.3 or 5.0
# Instantiate a OTP538U on analog pins A0 and A1
# A0 is used for the Ambient Temperature and A1 is used for the
# Object temperature.
# 512 et 513 remplacent 0 et 1 (mraa)
myTempIR = upmOtp538u.OTP538U(512, 513, OTP538U_AREF)

os.system("sudo ./Projet.sh")

while True:
	try:
		
		if Temps==0:
			Temps=Init()
			if (Temps==-1):
				break
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
		
		if (Temps==3):
			envoi_temp(str(Get_Temperature()).replace('.',','),1)
		elif(Temps==7):
			envoi_temp(str(Get_Temperature()).replace('.',','),2)
		else:
			print("Error")
		setText(" Decapsulage termine")
		time.sleep(2)
		if (Temps == 3):
			temperature_moyenne=wks1.cell(2,4).value.replace(',','.')
		if (Temps == 7):
			temperature_moyenne=wks2.cell(2,4).value.replace(',','.')
		setText(" Temperature moyenne : "+temperature_moyenne+" C")
		time.sleep(5)
		Temps=0
	
	except KeyboardInterrupt:
		grovepi.digitalWrite(relay,0)
		grovepi.digitalWrite(relayDC,0)
		grovepi.digitalWrite(buzzer,0)
		clearEcran()
		break
	except TypeError:
		print("Error1")
		grovepi.digitalWrite(relay,0)
		grovepi.digitalWrite(relayDC,0)
		grovepi.digitalWrite(buzzer,0)
		break
	except IOError:
		print("Error2")
		grovepi.digitalWrite(relay,0)
		grovepi.digitalWrite(relayDC,0)
		grovepi.digitalWrite(buzzer,0)		

setText(" Nombre de decapsulages : "+str(nb_decap()))
time.sleep(5)
setText(" A la prochaine !")
time.sleep(2)
grovepi.digitalWrite(relay,0)
grovepi.digitalWrite(relayDC,0)
grovepi.digitalWrite(buzzer,0)
clearEcran()
		
		
