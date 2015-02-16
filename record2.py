import numpy.fft
from struct import unpack
import numpy as np
import alsaaudio
import audioop
import time
from time import sleep
import RPi.GPIO as GPIO
import led

CARD = "Set"
max_bass = 0
index=1
frame_rate=15

import pyaudio
import sys

chunk = 512
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS, 
                rate=RATE, 
                input=True,
                output=True,
                frames_per_buffer=chunk)

def chunks(l, n):
    result = []
    for i in xrange(0, len(l), n):
        result.append(list(l[i:i+n]))
    return result

def getMaxValue(ys, n):
	columns = chunks(ys,int(len(ys)/n))
	maxValues = []
	for column in columns:
		maxValues.append(max(column))
	return maxValues

def updateMaxValues(newList, listToUpdate):
	for i in range(len(newList)):
		if newList[i] > listToUpdate[i]:
			listToUpdate[i] = newList[i]
	return listToUpdate

def calcColumnValues(currentValues,maxValues,rows):
	result = []
	for i in range(len(currentValues)):
		result.append(int(currentValues[i] / maxValues[i] * rows))
	return result

def fftt(data=None,trimBy=10,logScale=False,divBy=10):
        left,right=numpy.split(numpy.abs(numpy.fft.fft(data)),2)
        ys=numpy.add(left,right[::-1])
        if logScale:
            ys=numpy.multiply(20,numpy.log10(ys))
        xs=numpy.arange(512/2,dtype=float)
        if trimBy:
            i=int((512/2)/trimBy)
            ys=ys[:i]
            xs=xs[:i]*44100/512
        if divBy:
            ys=ys/float(divBy)
        return xs,ys

def getFrame(vals,columns,rows):
	frame = []
	for i in range(columns):
		row = []
		for j in range(rows):
			if j < vals[i]:
				row.append(1)
			else:
				row.append(0)
		frame.append(row)
	return frame	

globalMaxValues = []




while True:
	data_str = ""
	try:
		data_str = stream.read(chunk)
	except IOError:
		pass
	data = numpy.fromstring(data_str, dtype='int16')
	if len(data) > 511:
		result = numpy.abs(numpy.fft.rfft(data))
		result = numpy.delete(result,len(result)-1)
		k = np.array(result, copy=True) 
		a = int(k[index]/100000)
		if a > max_bass:
			max_bass = a
			print a
		freq = ""
		if max_bass > 0 and a > 0:
			final_val = int(5*int(a)/int(max_bass))
			for a in range(int(5*a/int(max_bass))):
				freq = freq + "#"
			print freq
	 		vals = []
			for i in range(4):
				vals.append(final_val)
			frame = getFrame(vals,4,4)
			if final_val > 0:
				led.draw(frame,frame_rate)
	
		#print xs
		
#		#ys[0] = ys[1]
#		m = getMaxValue(ys,4)
#		if len(globalMaxValues) != len(m):
#			print "aendern"
#			globalMaxValues = m
#		globalMaxValues = updateMaxValues(m,globalMaxValues)
#		vals =  calcColumnValues(m,globalMaxValues,4)
#		k = ""
#		for i in range(vals[1]):
#			k += "#"
#		#print vals
#		print k
#		print globalMaxValues 
#		for i in range(len(vals)):
#			vals[i] = int(vals[0])
#		#frame = [[1,0,0,0],[1,0,0,0],[1,0,0,0],[1,0,0]]
#		#for i in range((vals[0])-1):
#	#		for j in range(4):
	#			frame[j][i] = 1 
#		frame =  getFrame(vals,4,4)
#		led.draw(frame,5)
