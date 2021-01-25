##Maclaine Morham ADS1115 Solar MPPT Battery Amperage and Voltage Logging Python3 Code
#Dumps raw data into csv for later analysis>?
#Currently Calibration is Not Accurate Enough, Needs Further Calibration
#
import os
from os import path
from time import sleep, strftime, time
#CronTab Task Enableing
#import matplotlib as mpl
#mpl.use('Agg')
import matplotlib.pyplot as plt
import board
import busio
import datetime
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)
#What Data Do We Need to See?
Print = True #For Debugging and Calibration
Chart = False #Calibration Chart
#Set Slopes and Offsets format: (Value-Offset)*Slope
voltOffset = 0#ZeroVoltage Offset
voltSlope = 0.023494#0.0228401192#[jan1]0.0234945045#0.016985138#
ampsOffset = 20477.9#20510.1#16750
ampSlope = 0.002986#0.0034638##0.002986#0.00272
relayOffset = 0
relaySlope = 0.007846528
relayAmpOffset = 31163#Unlikely this is Correct
relayAmpSlope = 1
# Create the ADC object using the I2C bus
ads0 = ADS.ADS1115( i2c, address=0x4b )# Make Sure it's the right Address

# Create single-ended input on each channel 0-3
chan0 = AnalogIn(ads0, ADS.P0)
chan1 = AnalogIn(ads0, ADS.P1)
chan2 = AnalogIn(ads0, ADS.P2)
chan3 = AnalogIn(ads0, ADS.P3)

#LOG Data to CSV
def write_ADS():
    with open("/home/pi/ADS1115/ADS1115_RAWdata.csv", "a") as log:
        log.write("{0},{1},{2},{3},{4}\n".format(strftime("%Y-%m-%d %H:%M:%S"),chan0.value, chan1.value, chan2.value, chan3.value))
#Add Data Read Functionality?

plt.ion()
plt.figure(1, facecolor='lightgrey', edgecolor='darkblue', figsize=(6,25))
plt.title('Solar Pond Battery')
v0 = [] #Array for A0
v3 = [] #Array for A3
x = [] #Array for Time(s)
a = [] #Array for Calculated Amps
bv = [] #Array for Calculated Volts
#avx = [] #arrayfor3d
def graph():
    a.append(battamps)#AMPS - 24v
    bv.append(battvoltage)#VOLTS - 24v
    v0.append(relayAmps)#v0.append(chan0.value)#Fix Conditions Depending on Reading First
    v3.append(chan3.voltage)#v3.append(chan3.value)#Fix Conditions Depending on Voltage Reading First
    x.append(datetime.datetime.now())
    #x.append(time())
    plt.clf()
    plt.figure(1)
    #Calculated Battery Amps
    plt.subplot(2,1,1)
    plt.subplots_adjust(hspace=0.35)
    plt.subplots_adjust(top=0.95)
    plt.gcf().autofmt_xdate()
    plt.title("%.5s" % a[-1])
    plt.title('Battery Amperage', loc='left')
    #Decide Display Range
    if battamps > 5:
        plt.ylim(5,20)
    elif battamps < 0.5 and battamps > -0.5:
        plt.ylim(-6,10)
    elif battamps < -0.5:
        plt.ylim(-5.5,0)
    elif battamps < 2:
        plt.ylim(0,2)
    elif battamps < 5:
        plt.ylim(0,5)
    plt.gcf().autofmt_xdate()
    #plt.xlim(x[0],x[-1])
    plt.plot(x,a)
    #plt.xlabel("Time")
    plt.ylabel("Battery Amperage")
    #plt.text(x,a,"Time & Amps", horizontalalignment='right')
    #Calculated Battery Voltage PLOT
    plt.subplot(2,1,2)
    plt.subplots_adjust(bottom=0.08)
    plt.title("%.5s" % bv[-1])
    plt.title('Battery Voltage', loc='left')
    #Decide Display Range
    if battvoltage > 28:
        plt.ylim(28,30)
    elif battvoltage < 23.5:
        plt.ylim(22,24)
    elif battvoltage < 28:
        plt.ylim(22,28)
    plt.gcf().autofmt_xdate()
    plt.plot(x,bv)
    #plt.text(x,bv,"Time & Voltage",horizontalalignment='right')
    #plt.plot(x,v3)
    plt.ylabel("Battery Voltage")
    plt.xlabel("%.22s" % x[-1])
    #plt.xlabel('Date & Time:', loc='left')
    plt.savefig("/var/www/html/plot.png")
    #3D Graph Just Because
    #avx = plt.axes(projection='3d')
    #avx.plot3D(x, bv, a, 'yellow')
    #Relay Chart
    #plt.figure("Relay")
    #plt.subplot(2,1,1)
    #plt.plot(x,v0)
    #plt.plot(x,v0)
    #plt.xlabel("Time")
    #plt.ylabel("Amps-RAW")
    #plt.subplot(2,1,2)
    #plt.plot(x,v3)
    #plt.plot(x,v3)
    #plt.xlabel("Time")
    #plt.ylabel("Volts")
    #plt.title('Solar Pond Battery')
    plt.draw()
    #plt.close()
    #plt.savefig("/var/www/html/plot.png")

#try:
while True:
        battvoltage = chan1.value * voltSlope
        battamps = (chan2.value - ampsOffset) * ampSlope
        relayVoltage = chan3.value#(chan3.value - relayOffset) * relaySlope
        relayAmps = (chan0.value - relayAmpOffset) * relayAmpSlope
        #Should be able to use Relay Amps to determine grid status
        if Print == True:
            print("%.6s" % battvoltage," ", chan1.value, " ","%.6s" % battamps, " ", chan2.value, " ", chan0.value, " ", chan3.value,"%.4s" % abs(1/battamps),"%.21s" % datetime.datetime.now())
                            #print("A0=RAW:",chan0.value,"A1=RAW:",chan1.value,"A2=RAW:",chan2.value,"A3=RAW:",chan3.value) 
        write_ADS() #writes raw data to csv for analysis later hopefully
        graph() #runs graph program
        if battamps < 0.1 and battamps > -0.1:
            plt.pause(0.25)
            sleep(abs(1/battamps))
        else:
            plt.pause(0.25)
            sleep(0.25)
        #Insert 5:30am code, save image as date, clear array
        #if Hour
            #del x[:]
#except:
if path.exists('/var/www/html/plot.png'):
    os.system("sh /var/www/html/DayPlots/plotexit.sh")
    print("Exeption Caught: GoodBye")
else:
    print("plot.png Not Found. Goodbye.")
