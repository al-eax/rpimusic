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

print alsaaudio.mixers()
data_in =alsaaudio.PCM(alsaaudio.PCM_CAPTURE,alsaaudio.PCM_NONBLOCK,CARD)
print data_in.cardname()
data_in.setchannels(2)
data_in.setrate(44100)
data_in.setformat(alsaaudio.PCM_FORMAT_S16_LE)
data_in.setperiodsize(32)

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
def getLMH(xs,ys):
   av = numpy.mean(ys)
   low = []
   mid = []
   high = []
   for i in range(len(xs)):
      freq = xs[i]
      herz = ys[i]
      if freq <= 100:
         low.append([herz])
      if freq > 100 and freq < 1000:
         mid.append([herz])
      if freq > 1000:
         high.append([herz])
   
   lmax = 0
   mmax = 0
   hmax = 0
   for l in low:
      if l[0] > lmax:
        lmax = l[0]
   for m in mid:
      if m[0] > mmax:
        mmax = m[0]
   for h in high:
      if h[0] > hmax:
        hmax = h[0]
   return (lmax,mmax,hmax)
   #return (round( numpy.mean(low)  ) , round(numpy.mean(mid) ) , round(numpy.mean(high)) )

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
			if j <= vals[i]:
				row.append(1)
			else:
				row.append(0)
		frame.append(row)
	return frame	

globalMaxValues = []

while True:
	le,data = data_in.read()
	if le and len(data) > 511:
		a = numpy.fromstring(data[0:512], dtype='int16')
		xs,ys = fftt(a)
		#ys[0] = ys[1]
		m = getMaxValue(ys,4)
		if len(globalMaxValues) != len(m):
			print "aendern"
			globalMaxValues = m
		globalMaxValues = updateMaxValues(m,globalMaxValues)
		vals =  calcColumnValues(m,globalMaxValues,4)
		k = ""
		for i in range(vals[1]):
			k += "#"
		#print vals
#		print k
#		print globalMaxValues 
		for i in range(len(vals)):
			vals[i] = int(vals[0])
		#frame = [[1,0,0,0],[1,0,0,0],[1,0,0,0],[1,0,0]]
		#for i in range((vals[0])-1):
	#		for j in range(4):
	#			frame[j][i] = 1 
		frame =  getFrame(vals,4,4)
		led.draw(frame,5)
