# coding: utf-8
#------------- Importation des différentes librairies -------------#
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

#------------- Lancement du script qui allume l'écran ------------- #
os.system("sudo ./Projet.sh")


#------------- Connection à l'API google pour stocker les valeurs de nos décapsulages -------------#
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name('FASOconnexiongoogle.json',scope)

gc = gspread.authorize(credentials)

wks1 = gc.open("Temperature 1").sheet1
wks2 = gc.open("Temperature 2").sheet1

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# setOff :  -> Bool 
# La fonction setOff verifie si l'utilisateur appuie sur les deux boutons en même temps pendant au moins 2 secondes.
# Plus tard on utilisera cette fonction pour eteindre le programme 
def setOff():
	tmp_debut=time.time()
	tmp_fin=time.time()
	while tmp_fin-tmp_debut<2:
		tmp_fin=time.time()
		if grovepi.digitalRead(button1)==0 or grovepi.digitalRead(button2)==0:
			return False
	return True


# nb_decap:  -> Int
# La fonction nb_decap retourne le nombre de décapsulage depuis la mise en service du décapsuleur
def nb_decap():
	nb1=int(wks1.cell(3,5).value)
	nb2=int(wks2.cell(3,5).value)
	return nb1+nb2


# envoi_temp : Float x Int
# La fonction envoi_temp envoi dans le form la nouvelle temperature calculée lors du décapsulage
def envoi_temp(temperature,num):
	if (num == 1):
		requests.post('https://docs.google.com/forms/d/1KQa6qJuVxa7fWpZ3pcpd1S1MyM2B2OyjpYDz9uVt5w0/formResponse', data = {'entry.824402807':temperature},verify=False)
	if (num == 2):
		requests.post('https://docs.google.com/forms/d/1CV02WCQ15aaTsvUOA22GWnhpHbgEmU5XQaAGf3uDKew/formResponse', data = {'entry.1298687124':temperature},verify=False)
	if (num!=1 and num!=2):
		print("error")
		

# recevoir_temp_moyenne:  Float -> Float
# La fonction recevoir_temp_moyenne retourne la valeur de la temperature ideale pour notre décapsulage. Elle s'actualise en fonction
# des temperatures des bouteilles décapsulés jusque là. Et depend également du type de bouteille.
def recevoir_temp_moyenne(Temps): 
	if (Temps == 7.5):
		temperature_ideale=wks1.cell(4,4).value
	if (Temps == 7.5):
		temperature_ideale=wks2.cell(4,4).value
	if (Temps!=7.5 and Temps!=7.5):
		print("error")
		return -1
	return temperature_ideale


# Est_Bouteille_Posee  -> Bool
# La fonction Est_Bouteille_Posee verifie que la bouteille est posée sur le socle
def Est_Bouteille_Posee():
	if grovepi2.ultrasonicRead(ultrason)<8:
		return True
	else:
		return False

# Est_Bouteille_Posee_3  -> Bool
# La fonction Est_Bouteille_Posee_3 verifie que la bouteille est posée sur le socle depuis au moins 3 secondes
def Est_Bouteille_Posee_3():
	tmp_debut=time.time()
	tmp_fin=time.time()
	while tmp_fin-tmp_debut<3:
		tmp_fin=time.time()
		if not Est_Bouteille_Posee():
			return False
	return True
	
# Get_Temperature  -> Float
# La fonction Get_Temperature retourne la temperature de la bouteille
def Get_Temperature():
    	# Register exit handlers
    	#atexit.register(exitHandler)
    	#signal.signal(signal.SIGINT, SIGINTHandler)
        return(round(float(myTempIR.objectTemperature()),2))


	
# Est_Bouteille_Fraiche  Float -> Bool
# La fonction Est_Bouteille_Fraiche verifie que la bouteille est suffisament fraîche (la compare a la temperature ideale propre a son type de bouteille)
def Est_Bouteille_Fraiche(Temps):
	temperature_ideale=float(recevoir_temp_moyenne(Temps).replace(',','.'))
	temperature_bouteille=Get_Temperature()
	if (temperature_bouteille<temperature_ideale) :
		return True
	else:
		return False



# Choisir_Bouteille  -> Float
# La fonction Choisir_Bouteille demande a l'utilisateur de choisir le type de bouteille qu'il veut décapsuler
def Choisir_Bouteille():
	while True:
		if grovepi.digitalRead(button1)==1:
			return 7.5
		if grovepi.digitalRead(button2)==1:
			return 7.5



# Init  -> Int
# La fonction Init verifie si l'utilisateur ne veux pas eteindre le système, si la bouteille est posée depuis au moins 3 secondes et
# lui demande de choisir le type de bouteille qu'il veut decapsuler
def Init():
	if setOff():
		return -1
	if not Est_Bouteille_Posee():
		setText("    Poser  la      bouteille")
		return 0
	else:
		if not Est_Bouteille_Posee_3():
			return 0
		else:
			setText("     Choisir       bouteille")
			tmp=Choisir_Bouteille()
			return tmp




# Actionner  Float -> Int
# La fonction Actionner actionne le vérin pendant un temps rentré en paramètre et à tout moment si l'utilisateur enlève
# la bouteille, le vérin s'arrête brutalement de s'actionner.
def Actionner(Temps):
	tmp_debut=time.time()
	tmp_fin=time.time()
	while tmp_fin-tmp_debut<Temps:
		if not Est_Bouteille_Posee():
			return 0
		else:
			grovepi.digitalWrite(relay,1)
			grovepi.digitalWrite(relayDC,1)
			setText("   Decapsulage     en cours")
			tmp_fin=time.time()
	grovepi.digitalWrite(relay,0)
	return 1


# Actionner: Float
# La fonction Retracter retracte le verin pendant n secondes
def Retracter(Temps):
	grovepi.digitalWrite(relayDC,0)
	grovepi.digitalWrite(relay,1)
	time.sleep(Temps)
	grovepi.digitalWrite(relay,0)


# Decapsulage_Force  -> Bool
# La fonction Decapsulage_Force demande à l'utilisateur si il veut quand même décapsuler la bouteille ( si elle n'est pas fraîche)
def Decapsulage_Force():
	while True:
		if grovepi2.digitalRead(button1)==1:
			return True
		if grovepi2.digitalRead(button2)==1:
			return False



# TestTemperature  Float -> Int
# La fonction TestTemperature affiche la temperature, verifie si la bouteille est assez fraiche, si elle est fraiche on lance le decapsulage
# sinon on demande a l'utilisateur si il veut quand même décapsuler
def TestTemperature(Temps):
	if not Est_Bouteille_Fraiche(Temps):
		temperature=Get_Temperature()		
		setText(" Temperature :      " + str(temperature)+" C")
		time.sleep(3.5)
		setText("  Bouteille pas  assez fraiche")
		time.sleep(2.5)
		setText("   Quand meme    decapsuler ?")
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
		
		
		
# buzzer_fin:
# La fonction buzzer fin crée un signal sonore pour indiquer la fin du décapsulage
def buzzer_fin():
	grovepi.digitalWrite(buzzer,1)
	time.sleep(.5)
	grovepi.digitalWrite(buzzer,0)
	time.sleep(.5)
	grovepi.digitalWrite(buzzer,1)
	time.sleep(.5)
	grovepi.digitalWrite(buzzer,0)

#------------- Initialisation des pins ------------- #

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


# ------ Initialisation des pins 0 et 1 pour le capteur de température + déclaration de l'utilisation d'un shield à mraa ------ #
mraa.addSubplatform(mraa.GROVEPI, "0")
OTP538U_AREF = 5.0 # analog voltage, usually 3.3 or 5.0
# Instantiate a OTP538U on analog pins A0 and A1
# A0 is used for the Ambient Temperature and A1 is used for the
# Object temperature.
# 512 et 513 remplacent 0 et 1 (mraa)
myTempIR = upmOtp538u.OTP538U(512, 513, OTP538U_AREF)



while True:
	try:
		
		if Temps==0:
			Temps=Init()      #------------- Appel de la fonction Init qui retourne le temps
			if (Temps==-1):  #-------------d'activation du vérin en fonction du type de bouteille
				break               #-------------Si l'utilisateur appuie sur les deux boutons, on éteind le système 
			continue
		if TestTemperature(Temps)==0:  #-------------Verification que la bouteille est fraîche
			Temps=0
			continue
		if Actionner(Temps)==0: #------------- Lancement du décapsulage, si l'utilisateur enlève sa bouteille: Interruption 
			setText("  Interruption   Decapsulage")
			grovepi.digitalWrite(relay,0)		
			time.sleep(2)
			Retracter(Temps)  #------------- Si le décapsulage est interrompu on remet le vérin en position initiale
			Temps=0
			continue	
			
		grovepi.digitalWrite(relay,0) 
		time.sleep(2)
		Retracter(Temps) 
		buzzer_fin() #------------- Signal sonore qui indique la fin du décapsulage
		
		if (Temps==7.5):
			envoi_temp(str(Get_Temperature()).replace('.',','),1) #------------- Envoie des statistiques du décapsulage 
		elif(Temps==7.5):
			envoi_temp(str(Get_Temperature()).replace('.',','),2)
		else:
			print("Error")
		setText("   Decapsulage     termine")
		time.sleep(2)
		if (Temps == 7.5):		#------------- Calcul de la nouvelle moyenne de temperatures après ajout des nouvelles valeurs
			temperature_moyenne=wks1.cell(2,4).value.replace(',','.')
		if (Temps == 7.5):
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

#------------- Fin du programme, on affiche les stats puis on eteind l'écran et le vérin -------------#
setText(" Nombre de decapsulages : "+str(nb_decap()))
time.sleep(5)
setText(" A la prochaine       !")
time.sleep(2)
grovepi.digitalWrite(relay,0)
grovepi.digitalWrite(relayDC,0)
grovepi.digitalWrite(buzzer,0)
clearEcran()
os.system("sudo shutdown now") # On eteind la raspberry
		
