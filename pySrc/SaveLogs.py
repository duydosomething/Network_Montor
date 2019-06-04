import eel, os, time

# create log folder


def save_log():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        log_dir = os.path.join(base_dir, '..', "logs")
        print log_dir
        current_time = time.strftime("%Y-%m-%d_%H-%M-%S")
        OUTPUT_FOLDER = os.path.join(log_dir,current_time)
        os.makedirs(OUTPUT_FOLDER)
        result_log = os.path.join(OUTPUT_FOLDER, "Result-"+ current_time+".txt")
        router_info = eel.get_router_info()()
        
        output = str(eel.get_output()())
        
        fp = open(result_log,'w+')
        fp.seek(0)
        fp.write('Model Number: %s\n' % router_info['modelNumber'])
        fp.write('Hardware Version: %s\n' % router_info['hardwareVersion'])
        fp.write('Firmware: %s\n' % router_info['firmwareVersion'])
        fp.write('Serial Number: %s\n' % router_info['serialNumber'])
        

        fp.write(output)
        fp.close()
        return 'OK'
    except Exception as e:
        return e