import panel as pn
import os
import pandas as pd
import CANverter as canvtr
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter import Tk
import hvplot.pandas
import plotly.graph_objects as go
import traceback


pn.extension('plotly')
pn.extension('floatpanel')

time_field = 'Time (ms)'
whole_df = pd.DataFrame(columns=[time_field, 'y'])
canverter = None
log_file_path = ''
dbc_file_path = ''
csv_file_path = ''
project_options = [proj.split(".")[0] for proj in os.listdir("./PROJECTS/")]

pn.extension(template='fast')

Tk().withdraw()
root_path = os.path.expanduser("~")

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

def build_whole_df(selected_file_path, project_name):
    global whole_df
    global canverter

    whole_df = canverter.log_to_dataframe(selected_file_path)
    whole_df = whole_df.sort_values(by=time_field)
    whole_df.to_pickle("./PROJECTS/"+project_name+".project")

    # Interpolate all columns linearly based on the "time" column
    whole_df = whole_df.interpolate(method='linear', axis=0)
    all_columns = whole_df.columns.tolist()
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
    global whole_df
    global log_file_path
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
                    build_whole_df(log_file_path, project_name)
                    project_name_select.options = [proj.split(".")[0] for proj in os.listdir("./PROJECTS/")]
                    project_name_input_text.value = ""
            elif (file_extension == 'pkl'):
                print('pickle')
            elif (file_extension == 'csv'):
                print('csv')
            else:
                raise Exception
            file_selection[-1][-1]= ("Importing Successful!")
    except Exception as e:
        file_selection[-1][-1]= ("Importing Failed!")


    
def csv_file_picker_callback(event):
    global csv_file_path
    csv_file_path = asksaveasfilename(title = "Save Exported CSV File", filetypes = (("CSV Files","*.csv"),("all files","*.*")))
    csv_export_text.value = csv_file_path

def save_csv_callback(event):
    global whole_df
    global csv_file_path
    csv_file_path = csv_export_text.value
    if len(csv_export_selection[-1]) > 1:
        csv_export_selection[-1].pop(1)
    csv_export_selection[-1].append("Exporting Data...")
    try:
        whole_df.to_csv(csv_file_path)
        csv_file_path = ''
        csv_export_selection[-1][-1]= ("Export Successful!")
    except:
        csv_export_selection[-1][-1]= ("Export Failed!")
        
    
def export_data_panel(event):
    csv_export_text.placeholder = root_path
    user_input_block.append(pn.layout.FloatPanel(csv_export_selection, name='Export to CSV', height=300, width=500, contained=False, position="center"))
    if len(csv_export_selection[-1]) > 1:
        csv_export_selection[-1].pop(1)
    
def import_data_panel(event):
    user_input_block.append(pn.layout.FloatPanel(file_selection, name='Import Data', height=400, width=500, contained=False, position="center"))
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
export_data_panel_btn = pn.widgets.Button(name='Export Data', height=50)
export_data_panel_btn.on_click(export_data_panel)

# IMPORT_DATA FUNCTION WIDGETS
import_data_panel_btn = pn.widgets.Button(name='Import Data', height=50)
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
project_name_select = pn.widgets.Select(name='Select Project',options=project_options)
@pn.depends(project_name_select.param.value, watch=True)
def update_project(project_name_select):
    global whole_df
    column_select_choice.name = "Variables for "+project_name_select
    column_select_choice.value = []
    whole_df = pd.read_pickle("./PROJECTS/"+project_name_select+".project")
     # Interpolate all columns linearly based on the "time" column
    whole_df = whole_df.interpolate(method='linear', axis=0)
    all_columns = whole_df.columns.tolist()
    all_columns.remove(time_field)
    column_select_choice.options = all_columns
  
column_select_choice = pn.widgets.MultiChoice(name="Variables for "+project_name_select.value, value=[],
    options=[])

def clear_all_columns(event):
    column_select_choice.value = []

clear_all_columns_btn = pn.widgets.Button(name='Clear all columns', height=50)
clear_all_columns_btn.on_click(clear_all_columns)

def generate_plot(event):
    global whole_df
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
        pn.Row(save_csv_button)
    )
export_selection = pn.Row(
        project_name_select,
        import_data_panel_btn,
        export_data_panel_btn,
        height=100
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
    export_selection,
    plot_generation,
)

layout = pn.Row(
    user_input_block,
    plot_display
)

layout.servable()