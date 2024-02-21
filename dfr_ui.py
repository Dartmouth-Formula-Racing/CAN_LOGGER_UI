import panel as pn
import os
import pandas as pd
import CANverter as canvtr
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter import Tk
import plotly.graph_objects as go
import base64
import traceback
import pickle
from getcomponents import *
import constants

pn.extension('plotly')
pn.extension('floatpanel')
pn.extension('tabulator')

current_dataframe = pd.DataFrame(columns=[constants.TIME_FIELD, 'y'])
canverter = None
log_file_path = ''
dbc_file_path = ''
csv_file_path = ''
project_options = [proj.split(".")[0] for proj in os.listdir("./PROJECTS/")]
current_project_name = ''
favorites_options = [fav.split(".")[0] for fav in os.listdir("./FAVORITES/")]
button_height = 35

Tk().withdraw()
root_path = os.path.expanduser("~")

with open("DFRLOGO.png","rb") as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode("utf-8")

comb_axes_switch = pn.widgets.Switch(name='Switch')



def build_current_dataframe(selected_file_path, project_name):
    global current_dataframe
    global canverter

    current_dataframe = canverter.log_to_dataframe(selected_file_path)
    current_dataframe = current_dataframe.sort_values(by=constants.TIME_FIELD)
    current_dataframe.to_pickle("./PROJECTS/"+project_name+".project")

    interpolate_dataframe()
    

def interpolate_dataframe():
    global current_dataframe
    
    # Interpolate all columns linearly based on the "time" column

    if 'Time (s)' not in current_dataframe.columns:
        current_dataframe.insert(0, 'Time (s)', current_dataframe['Time (ms)'] / 1000)

    current_dataframe = current_dataframe.interpolate(method='linear', axis=0)
    all_columns = current_dataframe.columns.tolist()
    x_select_choice.options = all_columns

    columns_to_remove = ['Time (s)', 'Time (ms)']
    copy_current_dataframe = current_dataframe.drop(columns=columns_to_remove)
    y_columns = copy_current_dataframe.columns.tolist()
    column_select_choice.options = y_columns
    

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
    if len(log_import_selection[-1]) > 1:
        log_import_selection[-1].pop(1)
    log_import_selection[-1].append("Importing Data...")
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
                    project_name_select.options = [proj.split(".")[0] for proj in os.listdir("./PROJECTS/")]
                    project_name_input_text.value = ""
            elif (file_extension == 'pkl'):
                print('pickle')
            elif (file_extension == 'csv'):
                print('csv')
            else:
                raise Exception
            log_import_selection[-1][-1]= ("Importing Successful!")
    except Exception as e:
        traceback.print_exc()
        log_import_selection[-1][-1]= ("Importing Failed!")

def csv_file_picker_callback(event):
    global csv_file_path
    csv_file_path = asksaveasfilename(title = "Save Exported CSV File", filetypes = (("CSV Files","*.csv"),("all files","*.*")))
    csv_export_text.value = csv_file_path

def save_csv_callback(event):
    global current_dataframe
    global csv_file_path
    global current_project_name
    csv_file_path = csv_export_text.value
    if len(csv_export_selection[-1]) > 1:
        csv_export_selection[-1].pop(1)
    csv_export_selection[-1].append("Exporting Data...")
    try:
        if interpolate_csv_btn.value:
            current_dataframe.to_csv(csv_file_path)
        else:
            pd.read_pickle("./PROJECTS/"+current_project_name+".project").to_csv(csv_file_path)
        csv_file_path = ''
        csv_export_selection[-1][-1]= ("Export Successful!")
    except:
        csv_export_selection[-1][-1]= ("Export Failed!")
        
def export_data_panel(event):
    csv_export_text.placeholder = root_path
    update_float_display(float_panel_display, pn.layout.FloatPanel(csv_export_selection, name='Export to CSV', height=300, width=500, contained=False, position="center", theme="#00693e"))
    if len(csv_export_selection[-1]) > 1:
        csv_export_selection[-1].pop(1)
    
def import_data_panel(event):
    update_float_display(float_panel_display, pn.layout.FloatPanel(log_import_selection, name='Import Data', height=400, width=500, contained=False, position="center", theme="#00693e"))
    project_name_input_text.placeholder = "Project Name..."
    dbc_file_input_text.placeholder = root_path
    log_file_input_text.placeholder = root_path
    if len(log_import_selection[-1]) > 1:
        log_import_selection[-1].pop(1)

#CSV_EXPORT FUNCTION WIDGETS
csv_export_text = pn.widgets.TextInput(placeholder=root_path, height = 50, width = 300,align='center')
choose_csv_file_btn = pn.widgets.Button(name='Choose a file', height=50,align='center')
choose_csv_file_btn.on_click(csv_file_picker_callback)
save_csv_button = pn.widgets.Button(name='Save', height=50)
save_csv_button.on_click(save_csv_callback)
export_data_panel_btn = pn.widgets.Button(name='Export Data', align="center",height=35)
export_data_panel_btn.on_click(export_data_panel)
interpolate_csv_btn = pn.widgets.Checkbox(name='Interpolate Data')

# IMPORT_DATA FUNCTION WIDGETS
import_data_panel_btn = pn.widgets.Button(name='Import Data',align="center",height=35)
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
    
    column_select_choice.name = "Y Variables for "+project_name_select
    x_select_choice.name = "X Variable for "+project_name_select
    column_select_choice.value = []
    current_dataframe = pd.read_pickle("./PROJECTS/"+project_name_select+".project")
     # Interpolate all columns linearly based on the "time" column
    interpolate_dataframe()
    current_project_name = project_name_select

####################################################
def favorites_save_panel(event):
    if len(favorites_save_selection[-1]) > 1:
        favorites_save_selection[-1].pop(1)
    update_float_display(float_panel_display, pn.layout.FloatPanel(favorites_save_selection, name='Save Signal Grouping', height=200, width=500, contained=False, position="center", theme="#00693e"))

def favorites_del_panel(event):
    if len(favorites_del_selection[-1]) > 1:
        favorites_del_selection[-1].pop(1)
    update_float_display(float_panel_display, pn.layout.FloatPanel(favorites_del_selection, name='Save Signal Grouping', height=200, width=500, contained=False, position="center", theme="#00693e"))

def favorites_save(event):
    global favorites_select
    signals = column_select_choice.value

    if len(favorites_save_selection[-1]) > 1:
        favorites_save_selection[-1].pop(1)
    favorites_save_selection[-1].append("Saving Data...")

    if not os.path.exists('FAVORITES'):
        os.makedirs('FAVORITES')
    
    try:
        with open('./FAVORITES/'+ group_name.value + '.pkl','wb') as f:
            pickle.dump(signals,f)
        favorites_save_selection[-1][-1] = ('Saving Successful!')
    except:
        favorites_save_selection[-1][-1] = ('Saving Failed!')

    favorites_select.items = [fav.split(".")[0] for fav in os.listdir("./FAVORITES/")] #Update dropdown menu
    favorites_delete.options = [fav.split(".")[0] for fav in os.listdir("./FAVORITES/")]

def favorites_del(event):
    global favorites_select
    
    if len(favorites_del_selection[-1]) > 1:
        favorites_del_selection[-1].pop(1)
    favorites_del_selection[-1].append("Deleting Data...")

    try:
        os.remove('./FAVORITES/' + favorites_delete.value + '.pkl')
        favorites_del_selection[-1][-1] = ('Deleting Successful!')
    except:
        favorites_del_selection[-1][-1] = ('Deleting Failed!')

    favorites_select.items = [fav.split(".")[0] for fav in os.listdir("./FAVORITES/")] #Update dropdown menu
    favorites_delete.options = [fav.split(".")[0] for fav in os.listdir("./FAVORITES/")]

def favorites_load(event):
    with open('./FAVORITES/'+ favorites_select.clicked + '.pkl','rb') as f:
        column_select_choice.value = pickle.load(f)


favorites_select = pn.widgets.MenuButton(name='Signal Groupings',items=favorites_options, button_type='primary', sizing_mode="stretch_width")
favorites_select.on_click(favorites_load)

favorites_save_btn = pn.widgets.Button(name='Save Grouping', height=button_height, align="start")
favorites_save_btn.on_click(favorites_save_panel)

favorites_del_btn = pn.widgets.Button(name='Delete Grouping', height=button_height, align="start")
favorites_del_btn.on_click(favorites_del_panel)

group_name = pn.widgets.TextInput(name='', placeholder='Enter a name here...')
group_save_btn = pn.widgets.Button(name='Save', height=button_height, align="center")
group_save_btn.on_click(favorites_save)

group_del_btn = pn.widgets.Button(name='Delete', height=button_height, align="center")
group_del_btn.on_click(favorites_del)

favorites_delete = pn.widgets.Select(name='Signal Groupings', options=favorites_options)

favorites_save_selection = pn.Column(
    "Name your signal grouping. Be sure to use _ for spaces between words:",
    pn.Row(group_name),
    pn.Row(group_save_btn)
    )

favorites_del_selection = pn.Column(
    "Select a signal grouping to delete:",
    pn.Row(favorites_delete),
    pn.Row(group_del_btn)
    )
####################################################
  
column_select_choice = pn.widgets.MultiChoice(name="Y Variables for "+project_name_select.value, value=[],
    options=[], align="center")

x_select_choice = pn.widgets.Select(name="X Variable for "+project_name_select.value,options=[])

def clear_all_columns(event):
    column_select_choice.value = []

clear_all_columns_btn = pn.widgets.Button(name='Clear all columns', height=button_height, align="center")
clear_all_columns_btn.on_click(clear_all_columns)

def generate_plot(event):
    global current_dataframe
    plotly_pane.object = update_graph_figure(current_dataframe, column_select_choice.value, x_select_choice.value, comb_axes_switch.value)
    final_filter = column_select_choice.value.copy()
    final_filter.insert(0, constants.TIME_FIELD)
    update_tabulator_display(tabulator_display, pn.widgets.Tabulator(current_dataframe[final_filter], show_index = False, page_size=10, layout='fit_columns', sizing_mode='stretch_width'))

# Create an empty plot using hvplot
figure = update_graph_figure(current_dataframe, column_select_choice.value, x_select_choice.value, comb_axes_switch.value)
plotly_pane = pn.pane.Plotly(figure, sizing_mode="stretch_both", margin=10)

generate_plot_btn = pn.widgets.Button(name='Generate plot', height=button_height, align="center")
generate_plot_btn.on_click(generate_plot)
    
# Create a tabulator based on the data
log_import_selection = pn.Column(
    "Name your project, select .log file, and .dbc file",
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
        pn.layout.HSpacer(),
        import_data_panel_btn,
        pn.layout.HSpacer(),
        export_data_panel_btn,
        pn.layout.VSpacer(),
        pn.layout.HSpacer(),
        height=80,
    )

plot_generation_y = pn.Row(
    pn.layout.VSpacer(),
    column_select_choice,
    pn.layout.VSpacer(),
)

plot_generation_x = pn.Row(
    pn.layout.VSpacer(),
    x_select_choice,
    pn.layout.VSpacer(),
    height=80
)

comb_axes = pn.Row(
    pn.layout.VSpacer(),
    pn.widgets.StaticText(name='Combine Y-Axes', value=''),
    pn.widgets.TooltipIcon(value="Click the \"Generate plot\" button below to implement changes", width=20),
    comb_axes_switch,
    pn.layout.VSpacer(),
    height =30,
)

user_input_block = pn.Column(
    export_selection,
    pn.layout.VSpacer(),
    project_name_select,
    pn.layout.VSpacer(),
    pn.Tabs(
        ("Manual",
            pn.Column(
                pn.Row(
                    generate_plot_btn,
                    clear_all_columns_btn,
                ),
                pn.Row(
                favorites_select
                ),
                pn.Row(
                    favorites_save_btn,
                    favorites_del_btn,
                ),
                comb_axes,
                plot_generation_x,
                plot_generation_y,
                margin=(25, 10)
            )
        ),
        ( "Groupings",
            pn.Column(
                pn.layout.VSpacer(),

                pn.Row(
                favorites_select
                ),
                pn.Row(
                    pn.layout.VSpacer(),
                    favorites_save_btn,
                    favorites_del_btn,
                    pn.layout.VSpacer(),
                    pn.layout.HSpacer(),
                ),
                pn.layout.VSpacer(),
            ),
        )
    ),
    max_height=250,
)

template = pn.template.FastListTemplate(
    title="Dartmouth Formula Racing",
    logo=f"data:image/jpeg;base64,{encoded_string}",
    accent="#00693e",
    sidebar=user_input_block,
    prevent_collision=True,
    shadow=False
)

plot_display = pn.Row(plotly_pane, min_height=600, sizing_mode="stretch_both")
tabulator_display = constants.EMPTY_TABULATOR_DISPLAY
float_panel_display = constants.EMPTY_FLOAT_PANEL_DISPLAY

template.main.append(pn.Tabs(
    ("Visualize Projects", 
        pn.Column(
            plot_display,
            tabulator_display,
            float_panel_display
            )
        ), 
    ("Real-Time Plotting", 
        pn.Column())
    )
                     )

template.servable()
