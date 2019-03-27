import sys
sys.path.insert(1, '../../')
# Use latest version of Eel from parent directory

import os
import random
import jnaplib
import eel

@eel.expose
def getDeviceInfo():
    jnap = jnaplib.JnapClient()
    jnap.configure(url="http://192.168.20.1/JNAP", username="admin", password="admin")
    deviceInfo = {}
    allOutput = jnap.call("GetDeviceInfo")["output"]
    deviceInfo["firmwareVersion"] = allOutput["firmwareVersion"]
    deviceInfo["modelNumber"] = allOutput["modelNumber"]
    deviceInfo["hardwareVersion"] = allOutput["hardwareVersion"]
    deviceInfo["serialNumber"] = allOutput["serialNumber"]
    return deviceInfo

@eel.expose                         # Expose this function to JavaScript
def say_hello_py(x):
    # Print to Python console
    print('Hello from %s' % x)
    # Call a JavaScript function
    eel.say_hello_js('Python {from within say_hello_py()}!')


@eel.expose
def pick_file(folder):
    folder = os.path.expanduser(folder)
    if os.path.isdir(folder):
        return random.choice(os.listdir(folder))
    else:
        return '{} is not a valid folder'.format(folder)


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
