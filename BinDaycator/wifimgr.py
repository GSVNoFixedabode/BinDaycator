import network
import socket
import ure
import time

ap_ssid = "Bindicator"
ap_password = "bindicator"
ap_authmode = 3  # WPA2

NETWORK_PROFILES = 'wifi.dat'
ADDRESS_FILE = 'address'

wlan_ap = network.WLAN(network.AP_IF)
wlan_sta = network.WLAN(network.STA_IF)

server_socket = None

def do_connect(ssid, password):
    wlan_sta.active(True)
    if wlan_sta.isconnected():
        return None
    print('Trying to connect to %s...' % ssid)
    wlan_sta.connect(ssid, password)
    for retry in range(200):
        connected = wlan_sta.isconnected()
        if connected:
            break
        time.sleep(0.1)
        print('.', end='')
    if connected:
        print('\nConnected. Network config: ', wlan_sta.ifconfig())
        
    else:
        print('\nFailed. Not Connected to: ' + ssid)
    return connected

def send_header(client, status_code=200, content_length=None ):
    print(content_length)
    client.sendall("HTTP/1.0 {} OK\r\n".format(status_code))
    client.sendall("Content-Type: text/html\r\n")
    if content_length is not None:
      client.sendall("Content-Length: {}\r\n".format(content_length))
    client.sendall("\r\n")


def send_response(client, payload, status_code=200):
    content_length = len(payload)
    send_header(client, status_code, content_length)
    if content_length > 0:
        client.sendall(payload)
    client.close()
    
def get_connection():
    """return a working WLAN(STA_IF) instance or None"""
    # check if an address has been defined
    default_address = read_default_address()  # Read default address from file
    
    if default_address:
        print(default_address)
        
    # First check if there already is any connection:
    if wlan_sta.isconnected(): # and default_address:
        return wlan_sta

    connected = False
    try:
        # ESP connecting to WiFi takes time, wait a bit and try again:
        time.sleep(3)
        if wlan_sta.isconnected(): # and default_address:
            return wlan_sta
        print("Inside Try 1")
        # Read known network profiles from file
        profiles = read_profiles()

        # Search WiFis in range
        wlan_sta.active(True)
        networks = wlan_sta.scan()

        AUTHMODE = {0: "open", 1: "WEP", 2: "WPA-PSK", 3: "WPA2-PSK", 4: "WPA/WPA2-PSK"}
        for ssid, bssid, channel, rssi, authmode, hidden in sorted(networks, key=lambda x: x[3], reverse=True):
            ssid = ssid.decode('utf-8')
            encrypted = authmode > 0
            print("ssid: %s chan: %d rssi: %d authmode: %s" % (ssid, channel, rssi, AUTHMODE.get(authmode, '?')))
            if encrypted:
                if ssid in profiles:
                    password = profiles[ssid]
                    connected = do_connect(ssid, password)
                else:
                    print("skipping unknown encrypted network")
            else:  # open
                connected = do_connect(ssid, None)
            if connected:
                break
            print("Inside Try 2")
    except OSError as e:
        print("exception", str(e))

    # start web server for connection manager:
    if not connected:
        connected = start()

    return wlan_sta if connected else None

def read_profiles():
    with open(NETWORK_PROFILES) as f:
        lines = f.readlines()
    profiles = {}
    for line in lines:
        ssid, password = line.strip("\n").split(";")
        profiles[ssid] = password
    return profiles

def write_profiles(profiles):
    lines = []
    for ssid, password in profiles.items():
        lines.append("%s;%s\n" % (ssid, password))
    with open(NETWORK_PROFILES, "w") as f:
        f.write(''.join(lines))

def read_default_address():
    """Reads the address from the file or returns an empty string if the file doesn't exist."""
    try:
        with open(ADDRESS_FILE, "r") as f:
            return f.read().strip()
    except OSError:
        return ""  # Return empty string if file doesn't exist

def save_address(address):
    with open(ADDRESS_FILE, "w") as f:
        f.write(address)

def handle_root(client):
    wlan_sta.active(True)
    ssids = sorted(ssid.decode('utf-8') for ssid, *_ in wlan_sta.scan())
    default_address = read_default_address()  # Read default address from file

    send_header(client)
    client.sendall("""
        <html>
            <h1>Wi-Fi Client Setup</h1>
            <form action="configure" method="post">
                <table>
                    <tbody>
    """)
    while len(ssids):
        ssid = ssids.pop(0)
        client.sendall("""
                        <tr>
                            <td colspan="2">
                                <input type="radio" name="ssid" value="{0}" />{0}
                            </td>
                        </tr>
        """.format(ssid))
    client.sendall("""
                        <tr>
                            <td>Password:</td>
                            <td><input name="password" type="password" /></td>
                        </tr>
                        <tr>
                            <td>Address:</td>
                            <td><input name="address" type="text" value="{0}" /></td>
                        </tr>
                    </tbody>
                </table>
                <p>
                    <input type="submit" value="Submit" />
                </p>
            </form>
        </html>
    """.format(default_address))  # Insert the default address here
    client.close()

def handle_configure(client, request):
    match = ure.search("ssid=([^&]*)&password=([^&]*)&address=(.*)", request)

    if match is None:
        send_response(client, "Parameters not found", status_code=400)
        return False
    
    # version 1.9 compatibility
    try:
        ssid = match.group(1).decode("utf-8").replace("%3F", "?").replace("%21", "!")
        password = match.group(2).decode("utf-8").replace("%3F", "?").replace("%21", "!")
        address = match.group(3).decode("utf-8").replace("%3F", "?").replace("%21", "!").replace("+", " ")

    except Exception:
        ssid = match.group(1).replace("%3F", "?").replace("%21", "!")
        password = match.group(2).replace("%3F", "?").replace("%21", "!")
        address = match.group(3).replace("%3F", "?").replace("%21", "!").replace("+", " ")

    if len(ssid) == 0:
        send_response(client, "SSID must be provided", status_code=400)
        return False

    if len(address) == 0:
        send_response(client, "1-line address must be provided", status_code=400)
        return False
    else:
        save_address(address)

    if do_connect(ssid, password):
        send_response(client, "Connected successfully")
        try:
            profiles = read_profiles()
        except OSError:
            profiles = {}
        profiles[ssid] = password
        write_profiles(profiles)
        return True
    else:
        send_response(client, "Could not connect to WiFi")
        return False

def handle_not_found(client, url):
    send_response(client, "Path not found: {}".format(url), status_code=404)


def stop():
    global server_socket

    if server_socket:
        server_socket.close()
        server_socket = None


def start(port=80):
    global server_socket

    addr = socket.getaddrinfo('0.0.0.0', port)[0][-1]

    stop()

    wlan_sta.active(True)
    wlan_ap.active(True)

    wlan_ap.config(essid=ap_ssid, password=ap_password, authmode=ap_authmode)

    server_socket = socket.socket()
    server_socket.bind(addr)
    server_socket.listen(1)

    print('Connect to WiFi ssid ' + ap_ssid + ', default password: ' + ap_password)
    print('and access the ESP via your favorite web browser at 192.168.4.1.')
    print('Listening on:', addr)

    while True:
        if wlan_sta.isconnected():
            wlan_ap.active(False)
            return True

        client, addr = server_socket.accept()
        print('client connected from', addr)
        try:
            client.settimeout(5.0)

            request = b""
            try:
                while "\r\n\r\n" not in request:
                    request += client.recv(512)
            except OSError:
                pass

            # Handle form data from Safari on macOS and iOS; it sends \r\n\r\nssid=<ssid>&password=<password>
            try:
                request += client.recv(1024)
                print("Received form data after \\r\\n\\r\\n(i.e. from Safari on macOS or iOS)")
            except OSError:
                pass

            print("Request is: {}".format(request))
            if "HTTP" not in request:  # skip invalid requests
                continue

            # version 1.9 compatibility
            try:
                url = ure.search("(?:GET|POST) /(.*?)(?:\\?.*?)? HTTP", request).group(1).decode("utf-8").rstrip("/")
            except Exception:
                url = ure.search("(?:GET|POST) /(.*?)(?:\\?.*?)? HTTP", request).group(1).rstrip("/")
            print("URL is {}".format(url))

            if url == "":
                handle_root(client)
            elif url == "configure":
                handle_configure(client, request)
            else:
                handle_not_found(client, url)

        finally:
            client.close()