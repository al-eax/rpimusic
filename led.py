import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setmode(GPIO.BOARD)

GPIOPin = [3,5,3,5,7,26,24,21,19,23,8,10,11,12,13,15,16,18,22,13,3,18,5,6]

GPIO0 = 3
GPIO1 = 5
GPIO2 = 3
GPIO3 = 5
GPIO4 = 7
GPIO7 = 26
GPIO8 = 24
GPIO9 = 21
GPIO10 = 19
GPIO11 = 23
GPIO14 = 8
GPIO15 = 10
GPIO17 = 11
GPIO18 = 12
GPIO21 = 13
GPIO22 = 15
GPIO23 = 16
GPIO24 = 18
GPIO25 = 22
GPIO27 = 13
GPIO28 = 3
GPIO29 = 18
GPIO30 = 5
GPIO31 = 6


plus = [GPIO4,GPIO17,GPIO21,GPIO22]
minus= [GPIO18,GPIO23,GPIO24,GPIO25]


def LED(i,value):
	if value == 0:
		GPIO.output(i,GPIO.LOW)
	else:
		GPIO.output(i,GPIO.HIGH)
def OUT(i):
	GPIO.setup(i, GPIO.OUT)

def setLED(x,y):
	for p in range(len(plus)):
		if p == x:
			LED(plus[p],1)
		else:
			LED(plus[p],0)
	for m in range(len(minus)):
		if m == y:
			LED(minus[m],0)
		else:
			LED(minus[m],1)	
for p in plus:
	OUT(p)
	LED(p,0)
for p in minus:
	OUT(p)
	LED(p,0)


def draw(frame,times = 2000):
	for i in range(times):
		for x in range(len(frame)):
			for y in range(len(frame[x])):
				if(frame[x][y] == 1):
					setLED(x,y)
	for p in plus:
		LED(p,0)	
#	for m in minus:
#		LED(m,0)
def drawFrames(frames):
	for frame in frames:
		draw(frame)


def cleanup():
	GPIO.cleanup()
