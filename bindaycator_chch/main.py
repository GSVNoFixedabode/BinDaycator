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
#
#################################################
# BinDayCator micropython version for esp8266
# and 4 LEDs in 3D printed Wheelie bin
# Christchurch version
#################################################
#
# WS2812 LED strip Configuration
led_count = 4 # number of LEDs in strip
pin_no = 2 #pin number on board for D4

# colours
red = [255,0,0]
Garbage = red

green = [0,255,0]
Organic = green

yellow = [255,255,0]
Recycle = yellow

blue = [0,0,255]
black = [0,0,0]
white = [255,255,255]


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
#
########################
# Network Bits
########################
#pulsing('red')
#rainbow_cycle(1)
#pulsing('green')
#
#
def write_address(new):
    f1 = open("property", "w")
    f1.write(new)
    f1.close()
    
def get_address():
    try:
        f2 = open("property", "r")
        curr_property = f2.read()
        f2.close()
    except:
        curr_property = "82918"
        write_address(curr_property)
    return curr_property

def grabbinweek():
    import requests
    import os
    import json

# Read address file
    property = get_address()
    print(property)


# Call CCC site
    CCC_Call = "http://hyland.net.nz/oldsite/chch_bin_call.php?propertyid=" + property
    print(CCC_Call)
    r = requests.get(CCC_Call)
# Use one of these depending on what your response looks like:
    print(r.text)
    jdata = json.loads(r.text)
    # Extract material values
    material_values = [item['material'] for item in jdata]

# Print material values
    for material in material_values:
        print(material)

#    colour= jdata[0]['attributes']['CurrentWeek']  ### get the "y" or "b" part on return
#    colour = colour.replace("y","yellow")
#    colour = colour.replace("b","blue")
    r.close()
    return material_values

#### File data ###################################################


# And now for the main event
# On power on, turn LEDs red
for ii in range (led_count):
    np[ii] = red
np.write()
################ Network Start
wlan = wifimgr.get_connection()        #initializing wlan
if wlan is None:
    print("Could not initialize the network connection.")
    while True:
        pass  
print("ESP OK")
print('network config:', wlan.ifconfig())

################ Get current bin colours
week_colour = grabbinweek()

# Main loop for twiddling metaphorical thumbs
while True:

# Update 3 LEDs
    for x in range (led_count):
        y = x % 2
        print(x,y)
        week_index = globals()[week_colour[y]]
        np[x] = (week_index)
    np.write()
# Zzzzzzznp	
    time.sleep(5)
# pulse up then down
    for material in week_colour:
        material_index = globals()[material]
        pulsing(material_index)
    pulsing('white')
