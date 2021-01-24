from time import sleep, strftime, time
import matplotlib.pyplot as plt
import numpy as np
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)
#What Data Do We Need?
Print = True#For Debugging and Calibration
Chart = True#Calibration Chart
voltOffset = 0#
relayOffset = 0
ampsOffset = 20991#16750
#voltSlope
#ampSlope
# Create the ADC object using the I2C bus
ads0 = ADS.ADS1115( i2c, address=0x4b )# Make Sure it's the right Address
#ads1 = ADS.ADS1115( i2c, address=0x49 )

# Create single-ended input on each channel 0-3
chan0 = AnalogIn(ads0, ADS.P0)
chan1 = AnalogIn(ads0, ADS.P1)
chan2 = AnalogIn(ads0, ADS.P2)
chan3 = AnalogIn(ads0, ADS.P3)
# chan1 = AnalogIn(ads1, ADS.P1)
#LOG Data to CSV
def write_ADS():
    with open("/home/pi/ADS1115/ADS1115_RAWdata.csv", "a") as log:
    #with open("/home/pi/ADS1115/ADS1115_VOLTdata.csv", "a") as log:
        log.write("{0},{1},{2},{3},{4}\n".format(strftime("%Y-%m-%d %H:%M:%S"),chan0.value, chan1.value, chan2.value, chan3.value))
        #log.write("{0},{1},{2},{3},{4}\n".format(strftime("%Y-%m-%d %H:%M:%S"),chan0.voltage, chan1.voltage, chan2.voltage, chan3.voltage))
        #log.write("{0},{1}\n".format(strftime("%Y-%m-%d %H:%M:%S"),str(temp3)))

# Create differential input between channel 0 and 1
# chan = AnalogIn(ads, ADS.P0, ADS.P1)

plt.ion()
plt.figure(1)
plt.figure("Relay")
v0 = []#Array for A0
v1 = []
v2 = []
v3 = []
#y = []
x = []
a = []
v = []

def runningMeanFast(z, N):
    return np.convolve(z, np.ones((N,))/N)[(N-1):]

def graph():
    #amps = (chan2.voltage - 2.36) * 19.2
    #volts = (chan1.voltage) * 186.5 #186.5 24.2v nightime, no solar #184.4#triggered at 23.3
    
    amps = battamps
    volts = battvoltage
    a.append(amps)#AMPS - 24v
    v.append(volts)#VOLTS - 24v
    v0.append(chan0.value)#v0.append(chan0.voltage)#
    v1.append(chan1.value)#v1.append(chan0.voltage)
    v2.append(chan2.value)#v2.append(chan0.voltage)
    v3.append(chan3.voltage)#v3.append(chan0.value)#Fix Conditions Depending on Voltage Reading First
    x.append(time())
    plt.clf()
    #glow plug amps is very Stable ~2.5v ~= 24v. MPPT turns on inverter @ 25V State of Charge
    #plt.plot(x,v0)
    #24v battery voltage
    plt.figure(1)
    plt.subplot(2,1,1)
    if amps > 5:
        plt.ylim(5,20)
    elif amps < 0.5 && amps > -0.5:
        plt.ylim(-5,10)
    elif amps < -0.5:
        plt.ylim(-5,0)
    elif amps < 2:
        plt.ylim(0,2)
    elif amps < 5:
        plt.ylim(0,5)
    plt.plot(x,a)
    plt.xlabel("Time")
    #b = np.smooth(a, window='flat', window_len=11)
    #plt.plot(x,b)
    #plt.plot(runningMeanFast(a,N))
    #plt.plot(np.convolve(np.ones(200), np.ones(50)/50, mode='valid'));
    #plt.plot(x,cumsum)
    #plt.plot(x, cumsum)
    #plt.plot(x, moving_aves)
    plt.ylabel("Amps")
    #~2.50v ~= 0.5 Amps Charging, ~2.30v ~= 5A Dischargeing
    plt.subplot(2,1,2)
    if volts > 28:
        plt.ylim(28,30)
    elif volts < 24:
        plt.ylim(22,24)
    elif volts < 28:
        plt.ylim(22,28)
    plt.plot(x,v)
    plt.plot(x,v3)
    plt.ylabel("Battery Voltage")
    plt.xlabel("Time")
    #plt.subplot(2,1,3)#Didn't like this 3
    
    #Relay Chart
    if Chart == True:
    	plt.figure("Relay")
    	plt.subplot(2,1,1)
    	plt.plot(x,v0)
        plt.xlabel("Time")
        plt.ylabel("Amps-RAW")
    	plt.subplot(2,1,2)
    	plt.plot(x,v3)
        plt.xlabel("Time")
        #ylabel("Volts")
    plt.draw()

if Print == True:
    print("{:>5}\t{:>5}{:>5}\t{:>5}{:>5}\t{:>5}{:>5}\t{:>5}".format('raw0', 'v0', 'raw1', 'v1', 'raw2', 'v2', 'raw3', 'v3'))

while True:
    battvoltage = (chan1.value * .0234945045) - relayOffset #0.0234945045 = good while on Grid, Grid Relay on = 1453raw 0am
    #sleep(0.2)
    battamps = ((chan2.value - ampsOffset) * 0.0034638)#0.002986)#0.00272)#Needs to be slightly larger multiplyer 1/11/21 #jan10:offset:16884#attempt~offset:19050, new new offset: 17540, new offset:20103 multiplyer/slope:0.00272 #27.46 #13,884=2.35v??? #    
    #battvoltage = (chan1.value * voltageSlope) - voltageOffset
    #battamps = ((chan2.value - ampOffset) * ampSlope)
    relayVoltage = chan3.value * 0.0007846528
    relayCurrent = (chan0.value - 31163)#IF value is greater than 0, grid is off. else grid on
    if relayVoltage > 24:
         relayOffset = 10.1#Make this zero and correct multiplyer slope 
         #battAmpsCoeff = 0.00272
         ampsOffset = 20991#20668-20640->(Guessed with 0.5 inverter load, 0.5 solar for 0)#20991->(Recorded at night MPPT Load Disconnected)
         #voltageCurve = 0.0234945045
    elif relayVoltage < 20:
         relayOffset = 0
         voltageOffset = 0.0234945045#Original Slope
         ampsOffset = 20654##16800(OldValue)#20480(-0.5A Inverter Only)
         #battAmpsCoeff = 0.00349
         #voltageCurve = 0.0234945045
    #else:
         
         #print("Battery Within Window")
    write_ADS()
    graph()    
    if Print == True:
        #print("{:>5}\t{:>5.3f}{:>5}\t{:>5.3f}{:>5}\t{:>5.3f}{:>5}\t{:>5.3f}".format(chan0.value, chan0.voltage, chan1.value, chan1.voltage, chan2.value, chan2.voltage, chan3.value, chan3.voltage))
        print("{:.2f}"format(battvoltage), "{:2f}"format(battamps), chan1.value, chan2.value, "Amps:", chan0.value, "Volts:", chan3.value)
        #print("A0=RAW:",chan0.value,"A1=RAW:",chan1.value,"A2=RAW:",chan2.value,"A3=RAW:",chan3.value)
        #print(time())
    
    if amps < 0.25 && amps > -0.25:
        plt.pause(60)
    else:
        plt.pause(0.3)
    #print("{:>5}\t{:>5.3f}".format(chan0.value, chan0.voltage))
    #time.sleep(0.5)
    #print("{:>5}\t{:>5.3f}".format(chan1.value, chan1.voltage))
    #time.sleep(0.5)
    #print("{:>5}\t{:>5.3f}".format(chan2.value, chan2.voltage))
    #time.sleep(0.5)
    #print("{:>5}\t{:>5.3f}".format(chan3.value, chan3.voltage))
    #time.sleep(0.5)
    #print("{:>5}\t{:>5.3f}".format(chan1.value, chan1.voltage))
