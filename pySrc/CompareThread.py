import threading
import time
import eel
import nmap
import ipaddress
import socket
import netifaces


class CompareThread(threading.Thread):
    def __init__(self):
        super(CompareThread, self).__init__()
        self._stop_event = threading.Event()

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

    def run(self):
        print "running"
        nm = nmap.PortScanner()
        results = nm.scan(hosts=self.get_cidr(), arguments='-sn')['scan']
        prev_result_list = [key for key,value in results.iteritems()]
        while not self.stopped():
            none_removed = True
            none_added = True
            #print self._stop_event
            curr_results = nm.scan(hosts=self.get_cidr(), arguments='-sn')['scan']
            curr_result_list = [key for key,value in curr_results.iteritems()]
            for item in curr_result_list:
                if item not in prev_result_list:
                    eel.update_output('%s has been added\n' % item)
                    none_added = False
            for item in prev_result_list:
                if item not in curr_result_list:
                    eel.update_output('%s not found\n' % item)
                    none_removed = False
            if none_removed and none_added:
                eel.update_output('No changes were seen\n')
            #eel.update_output('FROM PYTHON\n')
            
            time.sleep(5)
