##Maclaine Morham ADS1115 Solar MPPT Battery Amperage and Voltage Logging Python3 Code
#Dumps raw data into csv for later analysis>?
#Currently Calibration is Not Accurate Enough, Needs Further Calibration
#
from time import sleep, strftime, time
import matplotlib.pyplot as plt
import board
import busio
import datetime.datetime.now()
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)
#What Data Do We Need to See?
Print = True #For Debugging and Calibration
Chart = True #Calibration Chart
#Set Slopes and Offsets format: (Value-Offset)*Slope
voltOffset = 0 
voltSlope = 0.016985138#0.00234945045#
ampsOffset = 20991#16750
ampSlope = 0.0034638##0.002986#0.00272
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
plt.figure(1, "Battery")
plt.figure("Relay")
v0 = []#Array for A0
v3 = []#Array for A3
x = []#Array for Time(s)
a = []#Array for Calculated Amps
bv = []#Array for Calculated Volts

def graph():
    a.append(battamps)#AMPS - 24v
    bv.append(battvoltage)#VOLTS - 24v
    v0.append(relayAmps)#v0.append(chan0.value)#Fix Conditions Depending on Reading First
    v3.append(chan3.voltage)#v3.append(chan3.value)#Fix Conditions Depending on Voltage Reading First
    x.append(datetime.datetime.now())
    plt.clf()
    plt.figure(1,"Battery")
    #Calculated Battery Amps
    plt.subplot(2,1,1)
    #Decide Display Range
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
    plt.gcf().autofmt_xdate()
    plt.plot(x,a)
    plt.xlabel("Time")
    plt.ylabel("Amps")
    #Calculated Battery Voltage PLOT
    plt.subplot(2,1,2)
    #Decide Display Range
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
    #Relay Chart
    plt.figure("Relay")
    plt.subplot(2,1,1)
    plt.plot(x,v0)
    plt.xlabel("Time")
    plt.ylabel("Amps-RAW")
    plt.subplot(2,1,2)
    plt.plot(x,v3)
    plt.xlabel("Time")
    plt.ylabel("Volts")
    plt.draw()


while True:
    battVoltage = (chan2.value - voltOffset) * voltSlope
    battamps = (chan1.value - ampsOffset) * ampSlope
    relayVoltage = (chan3.value - relayOffset) * relaySlope
    relayAmps = (chan0.value - relayAmpOffset) * relayAmpSlope
    #Should be able to use Relay Amps to Discern Grid Status:
    if relayVoltage > 20000:
         ampSlope = 0.0034638
         ampsOffset = 21029.9#20991#20668-20640->(Guessed with 0.5 inverter load, 0.5 solar for 0)#20991->(Recorded at night MPPT Load Disconnected)
         voltSlope = 0.016985138
    elif relayVoltage < 20001:
         voltageSlope = 0.0234945045#Original Slope
         ampsOffset = 20654.1##16800(OldValue)#20480(-0.5A Inverter Only)
         ampSlope = 0.00349
    #else:
         
         #print("Battery Within Window")
    write_ADS()
    graph()        
    if amps < 0.25 && amps > -0.25:
        plt.pause(1/battamps)
    else:
        plt.pause(0.5)
