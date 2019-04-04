import threading
import time

class CompareThread(threading.Thread):
    def __init__(self):
        super(CompareThread, self).__init__()
        self._stop_event = threading.Event()

    def stop(self):
        print "STOPPING THREAD"
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        print "running"

        while not self.stopped():
            #print self._stop_event
            print "THREAD IS STILL GOING"
            
            time.sleep(1)
