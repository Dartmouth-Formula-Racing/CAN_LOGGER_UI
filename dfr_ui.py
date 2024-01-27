import panel as pn
import os
import cantools
import pandas as pd
import CANverter as canvtr
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfilename
from tkinter import Tk
import hvplot.pandas
import plotly.graph_objects as go


pn.extension('plotly')

time_field = 'Time (ms)'
whole_df = pd.DataFrame(columns=[time_field, 'y'])
canverter = None
data_file_path = ''

pn.extension(template='fast')

Tk().withdraw()

pn.state.template.title = 'DFR UI'


def graphing():
    # df: csv data dataframe
    # y: list of attributes from csv we want to graph (dataframe headers)

    # Only handles up to 4...
    global whole_df
    ys = column_select_choice.value

    fig = go.Figure()

    if len(ys) == 0:
        return fig

    i=1
    for column_name in ys:
        fig.add_trace(go.Scatter(
            x=whole_df[time_field],
            y=whole_df[column_name],
            name=column_name,
            yaxis=f"y{i}"
        ))
        i=i+1
    
    fig.update_layout(
        xaxis=dict(domain=[0.2, 0.8], title="Time")
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
        title_text="multiple y-axes example",
        width=800,
    )

    return fig

def build_whole_df(selected_file_path):
    global whole_df
    global canverter
    
    whole_df = canverter.log_to_dataframe(selected_file_path)
    whole_df = whole_df.sort_values(by=time_field)

    # Interpolate all columns linearly based on the "time" column
    whole_df = whole_df.interpolate(method='linear', axis=0)
    all_columns = whole_df.columns.tolist()
    all_columns.remove(time_field)
    column_select_choice.options = all_columns
    whole_df.to_csv( "./SDCardDecodedAll.csv")
    file_input_text.value = 'Upload complete!'

def dbc_file_picker_callback(event):
    global whole_df
    global data_file_path
    global canverter
    selected_file_path = askopenfilename(title = "Select DBC File",filetypes = (("DBC Files","*.dbc"),("all files","*.*"))) 
    canverter = canvtr.CANverter(selected_file_path)
    if (data_file_path != '' and os.path.splitext(data_file_path)[1] == '.log'):
        build_whole_df(data_file_path)

def data_file_picker_callback(event):
    global canverter
    global whole_df
    global data_file_path
    data_file_path = askopenfilename(title = "Select Data File",filetypes = (("Data Files","*.log"),("all files","*.*"))) 

    # Get the file extension
    file_extension = os.path.splitext(data_file_path)[1]
    file_extension = file_extension.lower()

    if (file_extension == '.log'):
        if (canverter == None):
            print('Handle case later')
            file_input_text.value = "Please upload a DBC file to decode your log!"
        else:
            build_whole_df(data_file_path)
    elif (file_extension == '.pkl'):
        print('pickle')
    elif (file_extension == '.csv'):
        print('csv')
    else:
        raise Exception

# Create a FileInput widget and a Text widget
dbc_file_btn = pn.widgets.Button(name='Upload dbc file', height=50)
dbc_file_btn.on_click(dbc_file_picker_callback)

data_file_btn = pn.widgets.Button(name='Upload data file', height=50)
data_file_btn.on_click(data_file_picker_callback)

file_input_text = pn.widgets.TextInput(value="Upload your data!")

column_select_choice = pn.widgets.MultiChoice(name='ColumnSelect', value=[],
    options=[])

def clear_all_columns(event):
    column_select_choice.value = []

clear_all_columns_btn = pn.widgets.Button(name='Clear all columns', height=50)
clear_all_columns_btn.on_click(clear_all_columns)

def generate_plot(event):
    global whole_df

    print('in button handler')
    try:
        plotly_pane.object = graphing()
    except Exception as ex:
        raise ex

# Create an empty plot using hvplot
figure = graphing()

plotly_pane = pn.pane.Plotly(figure)

generate_plot_btn = pn.widgets.Button(name='Generate plot', height=50)
generate_plot_btn.on_click(generate_plot)

file_selection = pn.Column(
    "Select a new .log file or an old .csv or .pkl file.\nIf you want to upload a .log file, please first select the .dbc file you would like to use.",
    pn.Row(
        dbc_file_btn,
        data_file_btn,
        file_input_text,
    ),
    height=200
) 

plot_generation = pn.Row(
    column_select_choice,
    clear_all_columns_btn,
    generate_plot_btn,
    height=200
)

plot_display = pn.Row(
    plotly_pane,
    height=400
)

user_input_block = pn.Column(
    file_selection, 
    plot_generation
)

layout = pn.Row(
    user_input_block,
    plot_display
)

layout.servable()