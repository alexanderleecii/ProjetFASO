#! /usr/bin/python
import smbus
bus = smbus.SMBus(1)
addr= 0x02
obj= 0x07
v=bus.read_byte_data(addr,obj) 
w=bus.read_byte(obj) 
print v
print w