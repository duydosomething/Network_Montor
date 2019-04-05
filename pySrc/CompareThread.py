import threading
import time
import eel

class CompareThread(threading.Thread):
    def __init__(self):
        super(CompareThread, self).__init__()
        self._stop_event = threading.Event()

    def stop(self):
        print "STOPPING THREAD"
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    @eel.expose
    def run(self):
        print "running"

        while not self.stopped():
            #print self._stop_event
            eel.update_output('FROM PYTHON\n')
            
            time.sleep(1)
