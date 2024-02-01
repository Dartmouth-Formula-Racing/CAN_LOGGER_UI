import serial
import os
import traceback
import CANverter
from bokeh.plotting import figure, curdoc
from bokeh.driving import linear
import threading
import pandas as pd

tty_ports = os.listdir("/dev")
tty_ports = list(filter(lambda port: port.startswith("tty."), tty_ports))
for opt_num, port_name  in enumerate(tty_ports):
    print("["+ str(opt_num) + "] /dev/" + port_name)
port_option_num = input("Choose a port to connect to: ")
port_name = "/dev/" + tty_ports[int(port_option_num)]
print("Connecting to " + port_name + "...")

# configure the serial connections (the parameters differs on the device you are connecting to)
ser = serial.Serial(port=port_name, baudrate=12000000, timeout=1, xonxoff=False, rtscts=False, dsrdtr=True)        
canverter = CANverter.CANverter("./dbc/test.dbc")
new_data = pd.DataFrame()

def validate_message(message):
    validated_message = message.decode("utf-8")[:-1]
    return validated_message

p = figure()
r1 = p.line([], [], color="firebrick", line_width=2)
ds1 = r1.data_source

@linear()
def update(step):
    global new_data
    new_data = new_data.dropna()
    if (new_data.shape[0] != 0):
        data = new_data.iloc[0]
        ds1.data['x'].append(int(data[0]))
        ds1.data['y'].append(float(data[1]))
        ds1.trigger('data', ds1.data, ds1.data)
    new_data = pd.DataFrame()

curdoc().add_root(p)

# Add a periodic callback to be run every 500 milliseconds
curdoc().add_periodic_callback(update, 100)

def read_data():
    global new_data
    message = b''
    message_count = 0
    try :
        while True:
            message = ser.readline() 
            validated_message = validate_message(message)
            try: 
                try:
                    updatedData= canverter.decode_message_stream(validated_message)
                    new_data = pd.concat([new_data, updatedData])
                    new_data = new_data[['Time (ms)', 'X Axis Acceleration (g)']]
                    message_count += 1
                except:
                    pass
            except:
                print(traceback.format_exc())

    except :
        print(message_count)
        print(traceback.format_exc())
        print('Program exit !')
        pass

thread = threading.Thread(target=read_data)
thread.start()


