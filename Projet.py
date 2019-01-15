#coding: utf-8
import smbus
import time

bus = smbus.SMBus(1)  # pour I2C-1 (0 pour I2C-0)

# Indiquez ici les deux adresses de l'ecran LCD
# celle pour les couleurs du fond d'ecran 
# et celle pour afficher des caracteres
DISPLAY_RGB_ADDR = 0x62
DISPLAY_TEXT_ADDR = 0x3e


# Décommentez et completez le code de la fonction permettant de choisir
# la couleur du fond d'ecran, n'oubliez pas d'initialiser l'ecran
def setRGB(rouge,vert,bleu):
        # rouge, vert et bleu sont les composantes de la couleur demandée
        bus.write_byte_data(DISPLAY_RGB_ADDR,0x00,0x00)
        bus.write_byte_data(DISPLAY_RGB_ADDR,0x01,0x00)
        bus.write_byte_data(DISPLAY_RGB_ADDR,0x04,rouge) # <--- ?
        bus.write_byte_data(DISPLAY_RGB_ADDR,0x03,vert) # <--- ?
        bus.write_byte_data(DISPLAY_RGB_ADDR,0x02,bleu) # <--- ?
        bus.write_byte_data(DISPLAY_RGB_ADDR,0x08,0xAA)


def setColor(color):
        if color == "bleu":
                setRGB(0x00,0x00,0xFF)
        elif color == "vert":
                setRGB(0x00,0xFF,0x00)
        elif color == "rouge":
                setRGB(0xFF,0x00,0x00)
        elif color == "blanc":
                setRGB(0xFF,0xFF,0xFF)
        elif color == "noir":
                setRGB(0x00,0x00,0x00)
        else:
                print "Erreur 404"



# Envoie  a l'ecran une commande concerant l'affichage des caracteres
# (cette fonction vous est donnes gratuitement si vous
 # l'utilisez dans la fonction suivante, sinon donnez 2000€
# a la banque et allez dictement en prison :)
def textCmd(cmd):
    bus.write_byte_data(DISPLAY_TEXT_ADDR,0x80,cmd)

def textCmd2(cmd):
    bus.write_byte_data(DISPLAY_TEXT_ADDR,0x40,cmd)

def clearEcran():
	textCmd(0x01)
	textCmd(0x0F)
	textCmd(0x38)
	setRGB(0x00,0x00,0x00)
   
# Completez le code de la fonction permettant d'ecrire le texte recu en parametre
# Si le texte contient un \n ou plus de 16 caracteres pensez a gerer
# le retour a la ligne
def setText(texte):
        textCmd(0x01)
        textCmd(0x0F)
        textCmd(0x38)
	i=0
        j=0
        nligne=0
        # pour un caractere c a afficher :
        # bus.write_byte_data(DISPLAY_TEXT_ADDR,0x40,ord(c))
        # ...
        # si on rencontre \n ou si on depasse 16 caracteres
        #       textCommand(0xc0) # pour passer a la ligne
        while(i<len(texte)):
                if j==15:
                        textCmd(0xc0)
                        j=0
                        nligne=nligne+1
                elif nligne==2:
			time.sleep(5)
                        textCmd(0x01)
                        textCmd(0x0F)
                        textCmd(0x38)
			k=i-15
			while k<i:
				textCmd2(ord(texte[k]))
				k=k+1
			j=0
                        nligne=1
			textCmd(0xc0)
                elif texte[i]=='\n':
                        textCmd(0xc0)
                        j=0
                        nligne=nligne+1
                else:
                        textCmd2(ord(texte[i]))
               	 	i=i+1
			j=j+1
	

