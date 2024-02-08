import panel as pn
import os
import pandas as pd
import CANverter as canvtr
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter import Tk
import plotly.graph_objects as go
import base64
import traceback
import copy
import threading
import serial
import CANverter
from bokeh.plotting import figure as bokeh_figure
from bokeh.plotting import curdoc
from bokeh.driving import linear
from bokeh.models import ColumnDataSource
import traceback


pn.extension('plotly')
pn.extension('floatpanel')
pn.extension('tabulator')

time_field = 'Time (ms)'
proj_dir = "./PROJECTS/"
current_dataframe = pd.DataFrame(columns=[time_field, 'y'])
canverter = None
log_file_path = ''
dbc_file_path = ''
csv_file_path = ''

if not os.path.isdir(proj_dir):
    os.mkdir(proj_dir)

project_options = [proj.split(".")[0] for proj in os.listdir(proj_dir)]
current_project_name = ''

Tk().withdraw()
root_path = os.path.expanduser("~")

with open("dfr.jpeg","rb") as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode("utf-8")

comb_axes_switch = pn.widgets.Switch(name='Switch')

def graphing():
    # df: csv data dataframe
    # y: list of attributes from csv we want to graph (dataframe headers)

    # Only handles up to 4...
    global current_dataframe
    
    ys = column_select_choice.value
    switch = comb_axes_switch.value
    fig = go.Figure()

    if len(ys) == 0:
        return fig

    if switch:
        grouped_plots = {}
        y_labels = []
        for column_name in ys:
            units = column_name.split('(', 1)[1].split(')', 1)[0].strip()

            in_front = column_name.split('(')[0].split()[-1].strip()
            y_label = f"{in_front} ({units})"
            
            if y_label not in y_labels:
                y_labels.append(y_label)

            if units in grouped_plots:
                grouped_plots[units].append(column_name)
            else:
                grouped_plots[units] = [column_name] 
        
        ys = y_labels

        for i, units in enumerate(grouped_plots):
            for column_name in grouped_plots[units]:
                fig.add_trace(go.Scatter(
                    x=current_dataframe[time_field],
                    y=current_dataframe[column_name],
                    name=column_name,
                    yaxis=f"y{i+1}"
                ))   
        signal_num = len(grouped_plots)

    else:
        for i, column_name in enumerate(ys):
            fig.add_trace(go.Scatter(
                x=current_dataframe[time_field],
                y=current_dataframe[column_name],
                name=column_name,
                yaxis=f"y{i+1}"
            ))
        signal_num = len(ys)
    
    fig.update_layout(
        xaxis=dict(domain=[0.2, 0.8], title=time_field),
    )

    signal_num = len(ys)

    fig.update_layout(
        yaxis1=dict(
            title=ys[0],
        ),   
    )

    if signal_num >= 2:
        fig.update_layout(
            yaxis2=dict(
                title=ys[1],
                overlaying="y",
                side="right",
            ),   
        )
    
    
    if signal_num >= 3:
        fig.update_layout(
            yaxis3=dict(
                title=ys[2],
                anchor="free", 
                overlaying="y", 
                autoshift=True,
            ),   
        )
    
    if signal_num >= 4:
        fig.update_layout(
            yaxis4=dict(
                title=ys[3],
                anchor="free", 
                overlaying="y", 
                autoshift=True,
                side="right",
            ),   
        )    

    # Update layout properties
    fig.update_layout(
        width=800,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='left',
            x=0.1
        )
    )

    return fig

def build_current_dataframe(selected_file_path, project_name):
    global current_dataframe
    global canverter
    global proj_dir

    current_dataframe = canverter.log_to_dataframe(selected_file_path)
    current_dataframe = current_dataframe.sort_values(by=time_field)
    current_dataframe.to_pickle(proj_dir+project_name+".project")

    interpolate_dataframe()
    

def interpolate_dataframe():
    global current_dataframe
    
    # Interpolate all columns linearly based on the "time" column
    current_dataframe = current_dataframe.interpolate(method='linear', axis=0)
    all_columns = current_dataframe.columns.tolist()
    all_columns.remove(time_field)
    column_select_choice.options = all_columns
    

def dbc_file_picker_callback(event):
    global dbc_file_path
    global canverter
    dbc_file_path = askopenfilename(title = "Select DBC File",filetypes = (("DBC Files","*.dbc"),("all files","*.*"))) 
    dbc_file_input_text.value = dbc_file_path
    canverter = canvtr.CANverter(dbc_file_path)

def data_file_picker_callback(event):
    global log_file_path
    log_file_path = askopenfilename(title = "Select Data File",filetypes = (("Data Files","*.log"),("all files","*.*"))) 
    log_file_input_text.value = log_file_path
    
def import_data_callback(event):
    global canverter
    global current_dataframe
    global log_file_path
    global proj_dir
    if len(file_selection[-1]) > 1:
        file_selection[-1].pop(1)
    file_selection[-1].append("Importing Data...")
    try:
        # Get the file extension
        log_file_path = log_file_input_text.value
        file_extension = log_file_path.split(".")[-1].lower()
        project_name = project_name_input_text.value.replace(" ", "").lower()
        if project_name != None and project_name != '':
            if (file_extension == 'log'):
                if (canverter == None):
                    print('Handle case later')
                else:
                    build_current_dataframe(log_file_path, project_name)
                    project_name_select.options = [proj.split(".")[0] for proj in os.listdir(proj_dir)]
                    project_name_input_text.value = ""
            elif (file_extension == 'pkl'):
                print('pickle')
            elif (file_extension == 'csv'):
                print('csv')
            else:
                raise Exception
            file_selection[-1][-1]= ("Importing Successful!")
    except Exception as e:
        traceback.print_exc()
        file_selection[-1][-1]= ("Importing Failed!")

def csv_file_picker_callback(event):
    global csv_file_path
    csv_file_path = asksaveasfilename(title = "Save Exported CSV File", filetypes = (("CSV Files","*.csv"),("all files","*.*")))
    csv_export_text.value = csv_file_path

def save_csv_callback(event):
    global current_dataframe
    global csv_file_path
    global current_project_name
    global proj_dir
    csv_file_path = csv_export_text.value
    if len(csv_export_selection[-1]) > 1:
        csv_export_selection[-1].pop(1)
    csv_export_selection[-1].append("Exporting Data...")
    try:
        if interpolate_csv_btn.value:
            current_dataframe.to_csv(csv_file_path)
        else:
            pd.read_pickle(proj_dir+current_project_name+".project").to_csv(csv_file_path)
        csv_file_path = ''
        csv_export_selection[-1][-1]= ("Export Successful!")
    except:
        csv_export_selection[-1][-1]= ("Export Failed!")
        
def export_data_panel(event):
    csv_export_text.placeholder = root_path
    user_input_block.append(pn.layout.FloatPanel(csv_export_selection, name='Export to CSV', height=300, width=500, contained=False, position="center", theme="#00693e"))
    if len(csv_export_selection[-1]) > 1:
        csv_export_selection[-1].pop(1)
    
def import_data_panel(event):
    user_input_block.append(pn.layout.FloatPanel(file_selection, name='Import Data', height=400, width=500, contained=False, position="center", theme="#00693e"))
    project_name_input_text.placeholder = "Project Name..."
    dbc_file_input_text.placeholder = root_path
    log_file_input_text.placeholder = root_path
    if len(file_selection[-1]) > 1:
        file_selection[-1].pop(1)

#CSV_EXPORT FUNCTION WIDGETS
csv_export_text = pn.widgets.TextInput(placeholder=root_path, height = 50, width = 300,align='center')
choose_csv_file_btn = pn.widgets.Button(name='Choose a file', height=50,align='center')
choose_csv_file_btn.on_click(csv_file_picker_callback)
save_csv_button = pn.widgets.Button(name='Save', height=50)
save_csv_button.on_click(save_csv_callback)
export_data_panel_btn = pn.widgets.Button(name='Export Data', align="center",height = 50)
export_data_panel_btn.on_click(export_data_panel)
interpolate_csv_btn = pn.widgets.Checkbox(name='Interpolate Data')

# IMPORT_DATA FUNCTION WIDGETS
import_data_panel_btn = pn.widgets.Button(name='Import Data',align="center",height = 50)
import_data_panel_btn.on_click(import_data_panel)
dbc_file_btn = pn.widgets.Button(name='Upload .dbc file', height=50)
dbc_file_btn.on_click(dbc_file_picker_callback)
data_file_btn = pn.widgets.Button(name='Upload .log file', height=50)
data_file_btn.on_click(data_file_picker_callback)
dbc_file_input_text = pn.widgets.TextInput(placeholder=root_path)
log_file_input_text = pn.widgets.TextInput(placeholder=root_path)
project_name_input_text = pn.widgets.TextInput(name="Project Name", placeholder = "Project Name...")
import_data_button = pn.widgets.Button(name='Import Project', height=50)
import_data_button.on_click(import_data_callback)

#SELECT PROJECT FUNCTION WIDGETS
project_name_select = pn.widgets.Select(name='Select Project',options=project_options, align="center")
@pn.depends(project_name_select.param.value, watch=True)
def update_project(project_name_select):
    global current_dataframe
    global current_project_name
    global proj_dir
    column_select_choice.name = "Variables for "+project_name_select
    column_select_choice.value = []
    current_dataframe = pd.read_pickle(proj_dir+project_name_select+".project")
     # Interpolate all columns linearly based on the "time" column
    interpolate_dataframe()
    current_project_name = project_name_select

column_select_choice = pn.widgets.MultiChoice(name="Variables for "+project_name_select.value, value=[],
    options=[], align="center")
# column_select_choice = pn.widgets.MultiChoice(name="Please create/select a project.", value=[],
#     options=[], align="center")


def clear_all_columns(event):
    column_select_choice.value = []

clear_all_columns_btn = pn.widgets.Button(name='Clear all columns', height=50, align="center")
clear_all_columns_btn.on_click(clear_all_columns)

real_time_switch = pn.widgets.Switch(name='Switch')

def generate_plot(event):
    try:
        plotly_pane.object = graphing()
    except Exception as ex:
        raise ex

# Create an empty plot using hvplot
figure = graphing()

plotly_pane = pn.pane.Plotly(figure, sizing_mode="stretch_both")

generate_plot_btn = pn.widgets.Button(name='Generate plot', height=50, align="center")
generate_plot_btn.on_click(generate_plot)


def tabulation(event):
    global current_dataframe
    final_filter = column_select_choice.value.copy()
    final_filter.append(time_field)
    filtered_df = current_dataframe[final_filter]
    tabulator_display.pop(0)
    tabulator_display.append(pn.widgets.Tabulator(filtered_df, show_index = False))

# Create a tabulator based on the data
generate_plot_btn.on_click(tabulation)
tabulator_pane = pn.widgets.Tabulator(current_dataframe, show_index = False)

file_selection = pn.Column(
    "Name your project and select a new .log file or an old .csv or .pkl file.\nIf you want to upload a .log file, please first select the .dbc file you would like to use.",
    pn.Row(
        project_name_input_text,
    ),
    pn.Row(
        dbc_file_input_text,
        dbc_file_btn,
    ),
    pn.Row(
        log_file_input_text,
        data_file_btn,
        
    ),
    pn.Row(
        import_data_button
    ),
    height=300
) 
csv_export_selection = pn.Column(
        "Select the project you want to export into a .csv",
        pn.Row(project_name_select),
        pn.Row(csv_export_text, choose_csv_file_btn),
        pn.Row(interpolate_csv_btn),
        pn.Row(save_csv_button)
    )
export_selection = pn.Row(
        pn.layout.VSpacer(),
        project_name_select,
        import_data_panel_btn,
        export_data_panel_btn,
        pn.layout.VSpacer(),
        height=80
    )

plot_generation = pn.Row(
    pn.layout.VSpacer(),
    column_select_choice,
    clear_all_columns_btn,
    generate_plot_btn,
    real_time_switch,
    pn.layout.VSpacer(),
    height=80
)

comb_axes_text = pn.widgets.StaticText(name='Combine Y-Axes that have the same units', value='')
comb_axes_tt = pn.widgets.TooltipIcon(value="Click the \"Generate plot\" button below to implement changes")
comb_axes = pn.Row(
    comb_axes_text,
    comb_axes_switch,
    comb_axes_tt
)

plot_display = pn.Column(
    plotly_pane,
)

tabulator_display = pn.Row(
    tabulator_pane
)

user_input_block = pn.Column(
    pn.layout.VSpacer(),
    export_selection,
    comb_axes,
    plot_generation,
    pn.layout.VSpacer(),
    max_height=200,
)

template = pn.template.FastGridTemplate(
    title="DFR CAN UI",
    logo=f"data:image/jpeg;base64,{encoded_string}",
    accent="#00693e",
    background_color="#f3f0e4",
    row_height = 50
    )

template.main[:6, 0:12] = user_input_block
template.main[6:18, 0:12] = plot_display
template.main[18:23, 0:12] = tabulator_display

## Real time
def format_byte_message(message):
    formatted_msg = message.decode("utf-8")[:-1]
    return formatted_msg

@linear()
def update(step):
    global streaming_df
    with mutex:
        source.stream(streaming_df, rollover=roll_over)
        streaming_df = streaming_df.iloc[-roll_over:]

@pn.depends(real_time_switch.param.value, watch=True)
def start_reading_thread(real_time_switch_value):
    global plotly_pane
    if real_time_switch_value:
        plotly_pane = generate_bokeh_figure()
        thread = threading.Thread(target=read_data)
        thread.start()
    else:
        plotly_pane = pn.pane(graphing())

def read_data():
    global streaming_df
    try:
        while real_time_switch.value:
            message = ser.readline() 
            validated_message = format_byte_message(message)
            if validated_message != "":
                try: 
                    updatedData= canverter.decode_message_stream(validated_message)
                    with mutex:
                        streaming_df = pd.concat([streaming_df, updatedData])
                    print(streaming_df.tail())
                except:
                    print(validated_message)
                    print(traceback.format_exc())

    except:
        print(traceback.format_exc())
        print('Program exit !')
        pass

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
mutex = threading.Lock()

#initialize streaming_df
streaming_df = pd.DataFrame()
while True:
    try:
        message = ser.readline()
        validated_message = format_byte_message(message)
        if validated_message != "":
            streaming_df = canverter.decode_message_stream(validated_message)
            break
    except:
        pass

roll_over = 500

source = ColumnDataSource(streaming_df)

colors = ["red", "green", "blue",
          "orange", "purple", "black",
          "brown", "yellow"]

def generate_bokeh_figure():
    p = bokeh_figure(width=1400)
    # do we need to delete this later ? idk
    curdoc().add_root(p)

    # Add a periodic callback to be run every 500 milliseconds
    curdoc().add_periodic_callback(update, 100)
    # need to update column selection choices
    # need to regenerate when columns change...
    for (column, color) in zip(column_select_choice.value, colors):
        p.circle(x="Time (ms)", y=column, color = color, source=source)
    return pn.pane.Bokeh(p)

template.servable()
