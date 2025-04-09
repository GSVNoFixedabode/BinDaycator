import machine, neopixel
import time
import ntptime
import network
import wifimgr     # importing the Wi-Fi manager library
import gc
try:
  import usocket as socket
except:
  import socket
  
wlan = wifimgr.get_connection()        #initializing wlan

if wlan is None:
    print("Could not initialize the network connection.")
    while True:
        pass  
print("ESP OK")
print('network config:', wlan.ifconfig())
#
#################################################
# BinDayCator micropython version for esp8266
# and 4 LEDs in 3D printed Wheelie bin
#################################################
#
# WS2812 LED strip Configuration
led_count = 4 # number of LEDs in strip
pin_no = 2 #pin number on board for D4
weeknum = 0 # set global

# colours
red = [255,0,0]
green = [0,255,0]
blue = [0,0,255]
black = [0,0,0]
white = [255,255,255]
yellow = [255,255,0]
mauve = [207,132,120]
y_week = ["yellow", "green", "yellow", "green"]
b_week = ["red", "green", "blue", "green"]
err_week = ["red", "white", "red", "white"]
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

def fall(fcolour):
    fall_colour = globals()[fcolour]
    for ff in range (led_count):
        np[ff] = fall_colour
        np.write()
        time.sleep(0.1)
    time.sleep(0.5)
    
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
            elif colour == 'orange':
                np[k] = (j, 114, 230)
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
            elif colour == 'orange':
                np[kk] = (jj, 114, 23)
            elif colour == 'white':
                np[kk] = (jj, jj, jj)
            np.write()
#       time.sleep(0.05)   
#
########################
# Network Bits
########################
def do_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
       ## print('connecting to network...')
       ## wlan.connect('hyland_guest2g', 'hy1andkn0xr00neyb1ake')
        while not wlan.isconnected():
            ### give it another go 
            wlan = wifimgr.get_connection()  
            print("in network loop")
            ### still red
            pulsing('red')
            rainbow_cycle(1)

        ### add blinking  green LED routine
    print('network config:', wlan.ifconfig())
# On success pulse up then down
    pulsing('green')
#
#
def grabbinweek():
    import requests
    import os
    import json

# Read address file
    try:
        f1 = open("address", "r")
    # continue with the file.
    except OSError:  # open failed
        f1 = open("address", "w")
        f1.write("167 Signal Hill Road")
        f1.close

    f2 = open("address", "r")
    curr_address = f2.read()
    print(curr_address)

# Call DCC site
    DCC_Call = "https://www.dunedin.govt.nz/design/rubbish-and-collection-days-search/lookup/_nocache?query=" + curr_address
    DCC_Call = DCC_Call.replace(" ", "%20")
    print(DCC_Call)
    r = requests.get(DCC_Call)
# Use one of these depending on what your response looks like:
    print(r.text)

#If Site returned less than full string text
    if len(r.text) < 10:
        colour = 'red'
        return colour
    
    jdata = json.loads(r.text)
    colour= jdata[0]['attributes']['CurrentWeek']  ### get the "y" or "b" part on return
    colour = colour.replace("y","yellow")
    colour = colour.replace("b","blue")
    r.close()
    return colour

#### File data ###################################################


# And now for the main event
# On power on, turn LEDs red
for ii in range (led_count):
    np[ii] = red
np.write()
################ Network Start
#wlan = wifimgr.get_connection(7)        #initializing wlan
#if wlan is None:
#    print("Could not initialize the network connection.")
#    while True:
#        pass  
#print("ESP OK")
#print('network config:', wlan.ifconfig())
# 1. Get network connection
################ Network Start
do_connect()

################ Get current bin colour
week_colour = grabbinweek()

if week_colour == 'red':
    multi_colour = err_week
else:
    if week_colour == 'yellow':
        multi_colour = y_week
    else:
        multi_colour = b_week

# Main loop for twiddling metaphorical thumbs
while True:
#    week_colour = bin_day[weeknum]

#    print(weeknum)
#    old code commented out
#    print(week_colour)
#    week_index = globals()[week_colour]
   
#    print(week_index)    
# Update 3 LEDs
    for x in range (led_count):
        mcolour = multi_colour[x]
        week_index = globals()[mcolour]
        np[x] = (week_index)
    np.write()
# Zzzzzzznp	
    time.sleep(5)
# pulse up then down
#   pulsing(week_index)
    fall('mauve')
