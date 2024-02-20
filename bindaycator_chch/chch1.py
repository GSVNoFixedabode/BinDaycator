import machine, neopixel
import time
import ntptime
import network
import gc
try:
  import usocket as socket
except:
  import socket

def grabv2():
    import requests
    import os
    import json
    initial_timeout = 1000
    maximuml = 9000
    CCC_Call = "https://www.ccc.govt.nz/services/rubbish-and-recycling/collections/getProperty?ID=82918"
    r = requests.get(CCC_Call, stream=True, timeout=initial_timeout)
    r.raise_for_status()

    if int(r.headers.get('Content-Length')) > maximuml:
        raise ValueError('response too large')

    size = 0
    start = time.time()

    for chunk in r.iter_content(1024):
        if time.time() - start > receive_timeout:
            raise ValueError('timeout reached')

        size += len(chunk)
        if size > your_maximum:
            raise ValueError('response too large')

    # do something with chunk

def http_get(url):
    _, _, host, path = url.split('/', 3) #get the domain name and rest of the url
    addr = socket.getaddrinfo(host, 80)[0][-1] #get address for the domain.
    print(host)
    s = socket.socket() # create a socket.
    s.connect(addr) # connect to the remote machine using that socket
    # make an http request.
    s.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))

    while True:
        data = s.recv(100)# read the response, 100 bytes at a time.
        if data:
            print(str(data, 'utf8'), end='')
        else:
            break
    s.close()# close the socket.
    
def grabbinweek():
    import requests
    import os
    import json

# Call CCC site
    CCC_Call = "https://www.ccc.govt.nz/services/rubbish-and-recycling/collections/getProperty?ID=82918"
    r = requests.get(CCC_Call)
# Use one of these depending on what your response looks like:
    print(r.text)
#    jdata = json.loads(r.text)
#    colour= jdata[0]['attributes']['CurrentWeek']  ### get the "y" or "b" part on return
#    colour = colour.replace("y","yellow")
#    colour = colour.replace("b","blue")
    r.close()
def nextone():
    import requests
    headers = {'Accept': 'application/json'}
    CCC_Call = "https://www.ccc.govt.nz/services/rubbish-and-recycling/collections/getProperty?ID=82918"
    r = requests.get(CCC_Call, headers={'Accept': 'application/json'})

    print(f"Status Code: {r.status_code}, Content: {r.json()}")

    print(f"Response: {r.json()}")

#grabbinweek()
#grabv2()
#CCC_Call = "https://www.ccc.govt.nz/services/rubbish-and-recycling/collections/getProperty?ID=82918"    
#http_get(CCC_Call)
nextone()    
    