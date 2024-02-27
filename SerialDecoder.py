import serial
import os
import traceback
import CANverter
from bokeh.plotting import figure as bokeh_figure
from bokeh.plotting import curdoc
from bokeh.driving import linear
from bokeh.models import ColumnDataSource
import threading
import pandas as pd

roll_over = 500

tty_ports = os.listdir("/dev")
tty_ports = list(filter(lambda port: port.startswith("tty."), tty_ports))
for opt_num, port_name  in enumerate(tty_ports):
    print("["+ str(opt_num) + "] /dev/" + port_name)
port_option_num = input("Choose a port to connect to: ")
port_name = "/dev/" + tty_ports[int(port_option_num)]
print("Connecting to " + port_name + "...")

# configure the serial connections (the parameters differs on the device you are connecting to)
ser = serial.Serial(port=port_name, baudrate=12000000, timeout=1, xonxoff=False, rtscts=False, dsrdtr=True)        
canverter = CANverter.CANverter("./dbc/time_series.dbc")

def format_byte_message(message):
    formatted_msg = message.decode("utf-8")[:-1]
    return formatted_msg

df = pd.DataFrame()

while True:
    try:
        message = ser.readline()
        validated_message = format_byte_message(message)
        decoded_message = canverter.decode_message_stream(validated_message)
        if len(decoded_message) > 0:
            df = decoded_message
            break
    except:
        pass

p = bokeh_figure(width=1400)
source = ColumnDataSource(df)

selected_cols = ["X Axis Acceleration (g)", "Y Axis Acceleration (g)", "Z Axis Acceleration (g)",
                 "X Axis YawRate (deg/s)", "Y Axis YawRate (deg/s)", "Z Axis YawRate (deg/s)",
                 "GPS Latitude (degrees)", "GPS Longitude (degrees)"]

colors = ["red", "green", "blue",
          "orange", "purple", "black",
          "brown", "yellow"]

for (column, color) in zip(selected_cols, colors):
    p.circle(x="Time (ms)", y=column, color = color, source=source)

@linear()
def update(step):
    global df
    with mutex:
        source.stream(df, rollover=roll_over)
        df = df.iloc[-roll_over:]

curdoc().add_root(p)
# Add a periodic callback to be run every 500 milliseconds
curdoc().add_periodic_callback(update, 100)

def read_data():
    global df
    try:
        while True:
            message = ser.readline() 
            validated_message = format_byte_message(message)
            if validated_message != "":
                try: 
                    updatedData= canverter.decode_message_stream(validated_message)
                    with mutex:
                        df = pd.concat([df, updatedData])
                except:
                    print(validated_message)
                    print(traceback.format_exc())

    except :
        print(traceback.format_exc())
        print('Program exit !')
        pass

mutex = threading.Lock()
thread = threading.Thread(target=read_data)
thread.start()


