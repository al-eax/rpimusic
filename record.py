#import matplotlib.pyplot as plt
import numpy.fft
from struct import unpack
import numpy as np
import alsaaudio
import audioop
import time
from time import sleep
import RPi.GPIO as GPIO



#Define physical header pin numbers for 6 LEDs

# Set up audio
GPIO.setmode(GPIO.BCM)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(15, GPIO.OUT)
GPIO.setup(11,GPIO.OUT)
GPIO.setup(12,GPIO.OUT)
data_in =alsaaudio.PCM(alsaaudio.PCM_CAPTURE,alsaaudio.PCM_NORMAL,"LX3000")

data_in.setchannels(2)
data_in.setrate(44100)
data_in.setformat(alsaaudio.PCM_FORMAT_S16_LE)
data_in.setperiodsize(32)

normal_data = [ 4844 , 4844,  4231,  1727,   593,
   858 ,  487 ,  114 ,  211 ,   268,
   104.77414471 ,  133.5336344  ,  221.19605844 ,  185.46804012  , 163.4354632,
   144.96785024 ,  123.32038714 ,   80.89079171 ,   57.89928294  ,  84.98610859,
    70.9370193   ,  47.17688809,    50.89210726 ,   60.19769876   , 60.49098319]

#recentData = numpy.zeros(10)
#f, = plt.plot(range(0,256))
#plt.ion()
#plt.show()
#def plotData(data):
#   data[0] = 0
#   print len(range(0,256))
#   f.set_xdata(range(0,256))
#   f.set_ydata(data)
#   plt.draw()

def clean(ys):
   return ys
   for i in range(len(ys)):
      ys = round(pys[i] - normal_data[i])
   return ys

def LED(i,value):
   if value == 0:
      GPIO.output(i,GPIO.LOW)
   else:
      GPIO.output(i,GPIO.HIGH)


def getLMH2(ys):
   drittel = len(ys) / 3
   low = []
   mid = ys[drittel:2*drittel]
   high = ys[2*drittel:len(ys)]
   return (round(numpy.mean(low) / numpy.mean(normal_data[0:drittel]) ),
           round(numpy.mean(mid) / numpy.mean(normal_data[drittel:2*drittel])), 
           round(numpy.mean(high)/ numpy.mean(normal_data[2*drittel : len(low)])))

def getLMH(xs,ys):
   av = numpy.mean(ys)
   low = []
   low_n = []
   mid = []
   mid_n = []
   high = []
   high_n = []
   #ys = clean(ys)
   for i in range(len(xs)):
      freq = xs[i]
      herz = ys[i]
      if freq <= 150:
         low.append([herz])
         low_n.append([normal_data[i]])
      if freq > 150 and freq < 1000:
         mid.append([herz])
         mid_n.append([normal_data[i]])
      if freq > 1000:
         high.append([herz])
         high_n.append([normal_data[i]])
   l = 0 
   m = 0
   h = 0
   #print ys 
   fac = 5 
   for i in range(len(low)):
     if low[i] > av * fac:
         l = 1
   for i in range(len(mid)):
      if mid[i] > av*fac:
         m = 1
   for i in range(len(high)):
      if high[i] > av*fac:
        h = 1
   return (round(10 *  numpy.mean(low) / numpy.mean(low_n) ) , round(10 * numpy.mean(mid) / numpy.mean(mid_n)) , round(10 * numpy.mean(high) / numpy.mean(high_n)) )

def fftt(data=None,trimBy=10,logScale=False,divBy=100):
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

while True:
   # Read data from device
   l,data = data_in.read()
   print l
   if l and len(data) > 511:
     #print len(data)
     a = numpy.fromstring(data[0:512], dtype='int16')
     xs,ys = fftt(a)
     ys[0] = ys[1]
     print ys
     #(l,m,h) =  getLMH(xs,ys) 
     #print h 
     ##print ys[0:5]
     #print ys
     #if l > 13:
     #   print "bass"
     #   LED(12,1)
     #else :
     #   LED(12,0)
#
#     if m > 18 :
#        print "mid"
#        LED(11,1)
#     else:
#        LED(11,0)
#
#     if h > 10:
#        print "high"
#        LED(11,1)
#     else:
#        LED(11,0)
     time.sleep(0.1)
