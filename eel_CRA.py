import sys
sys.path.insert(1, '../../')
sys.path.insert(0, './pySrc/')
# Use latest version of Eel from parent directory

import os
import random
import jnaplib
import eel
import nmap
import ipaddress
import socket
import netifaces
import CompareThread


c = None

nm = nmap.PortScanner()
netmask = '/24'
cidr = ''
init_list = []
@eel.expose
def getDeviceInfo():
    default_gateway = get_ip_address()[0]
    jnap = jnaplib.JnapClient()
    jnap.configure(url="http://%s/JNAP" % default_gateway, username="admin", password="admin")
    
    deviceInfo = {}
    allOutput = jnap.call("GetDeviceInfo")["output"]
    deviceInfo["firmwareVersion"] = allOutput["firmwareVersion"]
    deviceInfo["modelNumber"] = allOutput["modelNumber"]
    deviceInfo["hardwareVersion"] = allOutput["hardwareVersion"]
    deviceInfo["serialNumber"] = allOutput["serialNumber"]
    return deviceInfo

@eel.expose
def start_compare():
    global c, init_list
    
    c = CompareThread.CompareThread(init_list)
    c.start()

@eel.expose()
def stop_compare():
    c.stop()
    c.join()

def get_cidr():
    curr_ip = get_ip_address()[1]
    return str(ipaddress.ip_network(unicode(curr_ip+netmask, 'utf-8'), strict=False))

def get_ip_address():
    gateways = netifaces.gateways()
    default_gateway = gateways['default'][netifaces.AF_INET][0]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    host_ip = s.getsockname()[0]
    return default_gateway, host_ip

@eel.expose
def get_scan_results():
    global init_list
    nm.scan(hosts=get_cidr(), arguments='-sn')
    init_dict = nm._scan_result['scan']
    init_list = [key for key,value in init_dict.iteritems()]
    
    
    return nm._scan_result['scan']

def start_eel(develop):
    """Start Eel with either production or development configuration"""
    if develop:
        directory = 'src'
        app = None
        page = {'port': 3000}
        flags = ['--auto-open-devtools-for-tabs']
    else:
        directory = 'build'
        app = 'chrome-app'
        page = 'index.html'
        flags = []

    eel.init(directory, ['.jsx', '.js', '.html'])

    print "Starting server..."
    eel.start(page, size=(1280, 800), options={
        'mode': app,
        'port': 8080,
        'host': 'localhost',
        'chromeFlags': flags
    })

if __name__ == '__main__':
    import sys

    # Pass any second argument to enable debugging. Production distribution can't receive arguments
    start_eel(develop=len(sys.argv) == 2)
