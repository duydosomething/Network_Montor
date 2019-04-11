import threading
import time
import eel
import nmap
import ipaddress
import socket
import netifaces
import datetime


class CompareThread(threading.Thread):
    def __init__(self, init_list):
        super(CompareThread, self).__init__()
        self._stop_event = threading.Event()
        self.init_list = init_list
        print self.init_list 

    def stop(self):
        print "STOPPING THREAD"
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def get_ip_address(self):
        gateways = netifaces.gateways()
        default_gateway = gateways['default'][netifaces.AF_INET][0]
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        host_ip = s.getsockname()[0]
        return default_gateway, host_ip

    def get_cidr(self):
        curr_ip = self.get_ip_address()[1]
        return str(ipaddress.ip_network(unicode(curr_ip+'/24', 'utf-8'), strict=False))

    def get_current_datetime(self):
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def run(self):
        print "running"
        nm = nmap.PortScanner()
        
        while not self.stopped():
            none_removed = True
            none_added = True
            
            curr_results = nm.scan(hosts=self.get_cidr(), arguments='-sn')['scan']
            curr_result_list = [key for key,value in curr_results.iteritems()]
            for item in curr_result_list:
                if item not in self.init_list:
                    eel.update_output('[%s] %s has been added\n' % (self.get_current_datetime(), item))
                    none_added = False
            for item in self.init_list:
                if item not in curr_result_list:
                    eel.update_output('[%s] %s not found\n' % (self.get_current_datetime(), item))
                    none_removed = False
            if none_removed and none_added:
                eel.update_output('[%s] No changes were seen\n' % self.get_current_datetime())
            
            
            time.sleep(5)
