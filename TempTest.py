#! /usr/bin/python
import smbus
bus = smbus.SMBus(1)
addr= 0x02
obj= 0x07
obj2=0x27
v=bus.read_byte_data(addr,obj) 
w=bus.read_byte(obj)
x=bus.read_byte_data(addr,obj2) 
y=bus.read_byte(obj2)
z=bus.read_byte(addr)
print v
print w
print x
print y
print z
