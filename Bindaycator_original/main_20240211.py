import machine, neopixel
import time
import ntptime
import network

#
#################################################
# BinDayCator micropython version for esp8266
# and 3 LEDs in 3D printed Wheelie bin
#################################################
#
# WS2812 LED strip Configuration
led_count = 3 # number of LEDs in strip
pin_no = 2 #pin number on board for D4
weeknum = 0 # set global

# Bin day by week, week 0 never used, weeks 1-52 sequencing blue yellow
# Once DCC switch to 2-bin system then will rework this
#2024 so far
bin_day = [
    'white',
    'blue','yellow','blue','yellow','blue','yellow','blue','yellow','blue','yellow',
    'blue','yellow','blue','yellow','blue','yellow','blue','yellow','blue','yellow',
    'blue','yellow','blue','yellow','blue','yellow','blue','yellow','blue','yellow',
    'blue','yellow','blue','yellow','blue','yellow','blue','yellow','blue','yellow',
    'blue','yellow','blue','yellow','blue','yellow','blue','yellow','blue','yellow','blue','yellow'
    ]
# colours
red = [255,0,0]
green = [0,255,0]
blue = [0,0,255]
black = [0,0,0]
white = [255,255,255]
yellow = [255,255,0]
#
############################################
# Functions for RGB Coloring
############################################
np = neopixel.NeoPixel(machine.Pin(pin_no), led_count)
#
def rainbow_cycle(wait):
    for j in range(255):
        for z in range(led_count):
            rc_index = (z * 256 // wait) + j
            np[z] = wheel(rc_index & 255)
        np.write()
        time.sleep_ms(10)

def wheel(pos):
#  Input a value 0 to 255 to get a color value.
#  The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    if pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    pos -= 170
    return (pos * 3, 0, 255 - pos * 3)

def pulsing(colour):
    for j in range (254):
        for k in range (led_count):
            if colour == 'green':
                np[k] = (0, j, 10)
            elif colour == 'yellow':
                np[k] = (j, j, 10)                
            elif colour == 'red':
                np[k] = (j, 10, 0) 
            elif colour == 'blue':
                np[k] = (0, 10, j)
            elif colour == 'white':
                np[k] = (j, j, j)
            np.write()
 #       time.sleep(0.05)
    for jj in range (254,1,-1):
        for kk in range (led_count):
            if colour == 'green':
                np[kk] = (0, jj, 10)
            elif colour == 'yellow':
                np[kk] = (jj, jj, 10)                
            elif colour == 'red':
                np[kk] = (jj, 10, 0) 
            elif colour == 'blue':
                np[kk] = (0, 10, jj)
            elif colour == 'white':
                np[kk] = (jj, jj, jj)
            np.write()
 #       time.sleep(0.05)   

########################
# Network Bits
########################
def do_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect('hyland_guest2g', 'hy1andkn0xr00neyb1ake')
        while not wlan.isconnected():
            print("in network loop")
            ### still red
            pulsing('red')
            rainbow_cycle(1)

        ### add blinking  green LED routine
    print('network config:', wlan.ifconfig())
# On success pulse up then down
    pulsing('green')
        

# Wibbly wobbly timey wimey bits
#####################################
    
def grabcurrentdate():
#if needed, overwrite default time server
    ntptime.host = "0.nz.pool.ntp.org"
    try:
  #make sure to have internet connection
        ntptime.settime()
        print("Local time after synchronization：%s" %str(time.localtime()))
    except:
        print("Error syncing time")
    week_num = int(time.localtime()[7]/7)
    return week_num

##################################################################
# And now for the main event
# On power on, turn LEDs red
for ii in range (led_count):
    np[ii] = red
np.write()
# 1. Get network connection
do_connect()
#2. GEt current true date and week number
weeknum = grabcurrentdate()

# Main loop for twiddling metaphorical thumbs
while True:
    week_colour = bin_day[weeknum]
    print(weeknum)
    print(week_colour)
    week_index = globals()[week_colour]
   
    print(week_index)    
# Update 3 LEDs
    for x in range (led_count):
        np[x] = (week_index)
    np.write()
# Zzzzzzznp	
    time.sleep(5)
# pulse up then down
    pulsing(week_index)
    pulsing('white')
