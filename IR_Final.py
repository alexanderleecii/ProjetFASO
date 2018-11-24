# coding: utf-8

import math
import time
import grovepi

SUR_TEMP_PIN = 0 # Analog input pin connect to temperature sensor SUR pin
OBJ_TEMP_PIN = 1 # Analog input pin connect to temperature sensor OBJ pin
temp_calibration=0 # this parameter was used to calibrate the temperature
objt_calibration=0.000 #this parameter was used to calibrate the object temperature
temperature_range=10 # we make a map of temperature-voltage according to sensor datasheet 10 is the temperature step when sensor and object distance is 9CM.
offset_vol=0.014 # this parameter was used to set the mid level voltage,when put the sensor in normal environment after 10 min
#the sensor output 0.For example,the surrounding temperature is 29，but the result is 27 via the sensor
#you should set the reerence to 0.520 or more,according to your sensor to change.
#the unit is V
tempValue = 0
objtValue= 0
current_temp=0
temp=0
temp1=0
temp2=0
temp3=0
reference_vol=0.500
clear_num=0 # when use lcd to display
R=0
voltage=0

res=[
318300,302903,288329,274533,261471,249100,237381,226276,215750,205768,
196300,187316,178788,170691,163002,155700,148766,142183,135936,130012,
124400,119038,113928,109059,104420,100000,95788,91775,87950,84305,
80830,77517,74357,71342,68466,65720,63098,60595,58202,55916,
53730,51645,49652,47746,45924,44180,42511,40912,39380,37910,
36500,35155,33866,32631,31446,30311,29222,28177,27175,26213,
25290,24403,23554,22738,21955,21202,20479,19783,19115,18472,
17260,16688,16138,15608,15098,14608,14135,13680,13242,12819,
12412,12020,11642,11278,10926,10587,10260,9945,9641,9347,
9063,8789,8525,8270,8023,7785,7555,7333,7118,6911]

obj=[
[0,-0.274,-0.58,-0.922,-1.301,-1.721,-2.183,-2.691,-3.247,-3.854,-4.516,-5.236],
[0.271,0,-0.303,-0.642,-1.018,-1.434,-1.894,-2.398,-2.951,-3.556,-4.215,-4.931],
[0.567,0.3,0,-0.335,-0.708,-1.121,-1.577,-2.078,-2.628,-3.229,-3.884,-4.597],
[0.891,0.628,0.331,0,-0.369,-0.778,-1.23,-1.728,-2.274,-2.871,-3.523,-4.232],
[1.244,0.985,0.692,0.365,0,-0.405,-0.853,-1.347,-1.889,-2.482,-3.13,-3.835],
[1.628,1.372,1.084,0.761,0.401,0,-0.444,-0.933,-1.47,-2.059,-2.702,-3.403],
[2.043,1.792,1.509,1.191,0.835,0.439,0,-0.484,-1.017,-1.601,-2.24,-2.936],
[2.491,2.246,1.968,1.655,1.304,0.913,0.479,0,-0.528,-1.107,-1.74,-2.431],
[2.975,2.735,2.462,2.155,1.809,1.424,0.996,0.522,0,-0.573,-1.201,-1.887],
[3.495,3.261,2.994,2.692,2.353,1.974,1.552,1.084,0.568,0,-0.622,-1.301],
[4.053,3.825,3.565,3.27,2.937,2.564,2.148,1.687,1.177,0.616,0,-0.673],
[4.651,4.43,4.177,3.888,3.562,3.196,2.787,2.332,1.829,1.275,0.666,0],
[5.29,5.076,4.83,4.549,4.231,3.872,3.47,3.023,2.527,1.98,1.379,0.72]
]

def binSearch(x): # this function used for measure the surrounding temperature
	low=0
	mid=0
	high=100
	while (low<=high):
		mid=(low+high)/2
		if(x<res[mid]):
			low= mid+1
		else:#(x>res[mid])
			high=mid-1

	return mid

def arraysearch(x,y): #x is the surrounding temperature,y is the object temperature
	i=0
	tem_coefficient=100 # Magnification of 100 times
	i=(x/10)+1 # Ambient temperature
	voltage=float(y)/tem_coefficient #the original voltage
	#print("sensor voltage: ")
	#print(voltage)
	#print("V")
	for temp3 in range(0,13):
		if((voltage>obj[temp3][i])and(voltage<obj[temp3+1][i])):
			return int(temp3)
		else :
			return temp3

def measureSurTemp():
	i=0
	current_temp1=0
	signal=0
	tempValue=0
	for i in range(0,10):
		tempValue+= grovepi.analogRead(SUR_TEMP_PIN)
		time.sleep(0.01)
	tempValue=tempValue/10
	temp = tempValue*1.1/1023
	R=2000000*temp/(2.50-temp)
	signal=binSearch(R)
	current_temp=signal-1+temp_calibration+(res[signal-1]-R)/(res[signal-1]-res[signal])
	#print("Surrounding temperature:")
	#print(current_temp)
	return current_temp

def measureObjectTemp():
	i=0
	j=0
	sur_temp=0
	array_temp=0
	final_temp=0
	objtValue=0
	for i in range(0,10):
		objtValue+= grovepi.analogRead(OBJ_TEMP_PIN)
		time.sleep(0.01)
	objtValue=objtValue/10 # Averaging processing
	temp1=objtValue*1.1/1023 # objt_calibration
	sur_temp=temp1-(reference_vol+offset_vol)
	#print("\n Sensor voltage:")
	#print(sur_temp)
	#print("V")
	array_temp=arraysearch(current_temp,sur_temp*1000)
	temp2=current_temp
	print(current_temp)
	print(array_temp)
	temp1=(temperature_range*voltage)/(obj[array_temp+1][int((temp2/10))+1]-obj[array_temp][int((temp2/10))+1])
	final_temp=temp2+temp1
	if((final_temp>100)or(final_temp<=-10)):
		print("\n out of range!")
	else:
		print("\n object temperature:")
		print(final_temp)
		

while True:
	measureSurTemp() # measure the Surrounding temperature around the sensor
	measureObjectTemp()
	time.sleep(1)
