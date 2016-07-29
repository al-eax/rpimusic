from bibliopixel.led import *
from bibliopixel.animation import StripChannelTest
from bibliopixel.drivers.LPD8806 import *

import numpy.fft
from struct import unpack
import numpy as np
import alsaaudio
import audioop
import time
from time import sleep


#create driver for a 12 pixels
led_width = 10 #columns
led_height = 16  #rows
driver = DriverLPD8806(led_width * led_height)
#driver = DriverLPD8806(16*4)
def cc(width , height ):
        result = []
        for w in range(width):
                line = []
                if w % 2 == 0:
                        line = range(w * height, (w+1)*height)
                else:
                        line = range((w+1)*height,w*height-1, -1)
                result.append(line)
        return result;

coords = cc(led_width, led_height)

led = LEDStrip(driver)


led.fillRGB(0,0,0)
for i in range(led_width*led_height):
	led.set(i,(100,200,50))
	led.update()
	sleep(0.01)
led.fillRGB(0,0,0)
led.update()
sleep(3)

for x in range(len(coords)):
	for y in range(len(coords[x])):
		led.set(coords[x][y],(0,200,100))
		led.update()


def draw(vals, coords, rgb = (100,200,240)):
	for x in range(len(coords)):
		for y in range(vals[x]):
			led.set(coords[x][y],rgb)
		for y in range(vals[x] , len(coords[x])):
			led.set(coords[x][y],(0,0,0))
	led.update()

CARD = "Set"


import pyaudio
import sys

chunk = 1024 
FORMAT = pyaudio.paInt16
CHANNELS = 1 

RATE = 44100

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS, 
                rate=RATE, 
                input=True,
                output=True,
                frames_per_buffer=chunk)



def fftt2(data):
	data *= numpy.hanning(len(data))

	fourier = np.fft.rfft(data)
	fourier = np.delete(fourier, len(fourier) - 1)
	fourier = np.abs(fourier) ** 2
	return fourier

def fftt(data,trimBy=False,logScale=True,divBy=False):
	data *= numpy.hanning(len(data))
	left,right=numpy.split(numpy.abs(numpy.fft.fft(data)),2)
        ys=numpy.add(left,right[::-1])
        if logScale:
            ys=numpy.multiply(20,numpy.log10(ys))
        xs=numpy.arange(chunk/2,dtype=float)
        if trimBy:
            i=int((chunk/2)/trimBy)
            ys=ys[:i]
            xs=xs[:i]*RATE/chunk
        if divBy:
            ys=ys/float(divBy)
	return ys,xs


#cut l into n peaces
def chunks(l, number):
	n = int(len(l) / number)
	result = []
	for i in xrange(0, len(l), n):
		result.append(list(l[i:i+n]))
	if len(result) > number:
		result = result[0:number]
	return result

#cut ys into n peaces and get max values from each peace
def getMaxValue(ys, n):
	columns = chunks(ys,n)
	maxValues = []
	if len(columns) != n:
		print "!!!!! WARNUNG !!!!"
		print str(n) + " != " + str(len(columns))
	for column in columns:
		maxValues.append((numpy.sum(column)))
	return maxValues

#check if values from newList are higher than from listToUpdate
def updateMaxValues(newList, listToUpdate):
	for i in range(len(newList)):
		if newList[i] > listToUpdate[i]:
			listToUpdate[i] = newList[i]
	return listToUpdate


def calcColumnValues(currentValues,maxValues,rows):
	result = []
	for i in range(len(currentValues)):
		if maxValues[i] == 0:
			result.append(0)
		else:
			result.append(int(currentValues[i] / maxValues[i] * rows))
	return result


def cutHZ(ys,HZ,beginHZ,endHZ):
    beginScale = beginHZ/float(HZ)
    endScale = endHZ/float(HZ)
    l = len(ys)
    beginIndex = l*beginScale
    endIndex = l*endScale
    return ys[int(beginIndex) : int(endIndex)]


def getRauschenAverate(dauer=100):
    rauschen = numpy.array([])
    for i in range(dauer):
        try:
            data = stream.read(chunk)
            if len(rauschen) == 0:
                rauschen = numpy.fromstring(data, dtype=numpy.int16)
            else:
                rauschen += numpy.fromstring(data, dtype=numpy.int16)
        except IOError:
            pass
    for i in range(len(rauschen)):
        rauschen[i] = rauschen[i] / dauer
    return rauschen
rauschen = getRauschenAverate()

def cut2(ys,beginHZ,endHZ):
	maxHZ = 19300.0
	beginScale = beginHZ / maxHZ
	endScale = endHZ / maxHZ
	l = len(ys)
	beginIndex = int(l * beginScale)
	endIndex = int(l* endScale)
	return ys[beginIndex : endIndex]

globalMaxValues = []

bass_max = []
normal_max = []
height_max = []

colorTable = [(100,100,100) , (100,100,250) , (1,100,250),
		(1,1,250), (250,1,250), (250,1,1),
		(250,1,1),(250,100,1),(250,100,100)]
colorIndex = 0
color = colorTable[colorIndex]

lastValues = []

maxDB = 0

while True:
	data = ""
	try:
		data = stream.read(chunk)
	except IOError:
		pass
	#le,data = data_in.read()
	data = numpy.fromstring(data, dtype=numpy.int16)
	if len(data) == chunk :
		#data -= rauschen
		ys,xs = fftt(data)

		ys = ys**4

		db = numpy.average(ys)
		if db > maxDB:
			maxDB = db		

		bass = cut2(ys,0,500)
		normal = cut2(ys,500,1000)
		height = cut2(ys,1000,8000)
		
	
		mat_bass = getMaxValue(bass,4)
                mat_normal = getMaxValue(normal,4)
                mat_height = getMaxValue(height,2)


		if len(bass_max) == 0:
                        bass_max = mat_bass
                if len(normal_max) == 0:
                        normal_max = mat_normal
                if len(height_max) == 0:
                        height_max = mat_height


		bass_max = updateMaxValues(mat_bass,bass_max)
		normal_max = updateMaxValues(mat_normal, normal_max)
		height_max = updateMaxValues(mat_height, height_max)


		#0 bi2 29 = 0 bis 1700 HZ
			
		#for i in range(len(ys)):
	        #	ys[i] = ys[i] * ys[i] * ys[i] * ys[i] * ys[i]
		#m = getMaxValue(ys,led_width)
		#if len(globalMaxValues) != len(m):
		#	globalMaxValues = m
		#globalMaxValues = updateMaxValues(m,globalMaxValues)
		m = np.concatenate((mat_bass, mat_normal , mat_height))
		m2 = np.concatenate((bass_max , normal_max , height_max))
		
		vals =  calcColumnValues(m,m2,led_height)
		
		rt,gt,bt = colorTable[colorIndex]
		r,g,b = color
		if r < rt:
			r += 1
		if r > rt:
			r -= 1
		if b < bt:
			b += 1
		if b > bt:
			b -= 1
		if g < gt:
			g += 1
		if g > gt:
			g -= 1
		color = (r,g,b)
		if color == colorTable[colorIndex]:
			colorIndex +=1
		if colorIndex == len(colorTable):
			colorIndex = 0 
		vals.reverse()
		#led.setMasterBrightness(int(db/float(maxDB) * 250))
		if len(lastValues) == 0:
			lastValues = vals
		draw(vals,coords,color)
		'''while lastValues != vals:
			for i in range(len(vals)):
				if vals[i] > lastValues[i]:
					lastValues[i] = vals[i] 
				if vals[i] < lastValues[i]:
					lastValues[i] -= 1
			draw(lastValues,coords,color)'''
