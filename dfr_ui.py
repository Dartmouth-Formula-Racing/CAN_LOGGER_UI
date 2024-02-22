import panel as pn
import os
import pandas as pd
import CANverter as canvtr
import projects
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter import Tk
import traceback
import pickle
from getcomponents import *
from constants import *
import json
from pprint import pprint

pn.extension('plotly')
pn.extension('floatpanel')
pn.extension('tabulator')
#pn.extension(design='material', global_css=[':root { --design-primary-color: "#00693e"; }'])

curr_project = projects.Project(TIME_FIELD)
time_series_canverter = None
message_canverter = None
log_file_path = ''
csv_file_path = ''
project_options = get_projects()
current_project_name = ''
favorites_options = get_favorites()
Tk().withdraw()

def build_current_project(log_file_path, project_name):
    global curr_project
    global time_series_canverter
    global message_canverter

    curr_project.ts_dataframe = time_series_canverter.log_to_dataframe(log_file_path)
    curr_project.ts_dataframe = curr_project.ts_dataframe.sort_values(by=TIME_FIELD)
    msg_df = message_canverter.log_to_dataframe(log_file_path).sort_values(by=TIME_FIELD).set_index(TIME_FIELD)
    curr_project.store_msg_df_as_dict(msg_df)
    with open("./PROJECTS/"+project_name+".project", 'wb') as f:
        pickle.dump(curr_project, f)

    interpolate_dataframe()
    
def interpolate_dataframe():
    global curr_project

    if 'Time (s)' not in curr_project.ts_dataframe.columns:
        curr_project.ts_dataframe.insert(0, 'Time (s)', curr_project.ts_dataframe['Time (ms)'] / 1000)

    curr_project.ts_dataframe = curr_project.ts_dataframe.interpolate(method='linear', axis=0)
    all_columns = curr_project.ts_dataframe.columns.tolist()
    x_axis_field_select.options = all_columns

    columns_to_remove = ['Time (s)', 'Time (ms)']
    copy_current_dataframe = curr_project.ts_dataframe.drop(columns=columns_to_remove)
    y_columns = copy_current_dataframe.columns.tolist()
    y_axes_field_multiselect.options = y_columns
    
"""
############################ COMPONENT CALLBACKS ##################################
"""
def time_series_dbc_file_btn_callback(event):
    global time_series_canverter
    time_series_dbc_file_path = askopenfilename(title = "Select Time Series DBC File",filetypes = (("DBC Files","*.dbc"),("all files","*.*"))) 
    if time_series_dbc_file_path != '':
        time_series_dbc_file_input_text.value = time_series_dbc_file_path
        time_series_canverter = canvtr.CANverter(time_series_dbc_file_path)

def message_dbc_file_btn_callback(event):
    global message_canverter
    message_dbc_file_path = askopenfilename(title = "Select Message DBC File",filetypes = (("DBC Files","*.dbc"),("all files","*.*"))) 
    if message_dbc_file_path != '':
        message_dbc_file_input_text.value = message_dbc_file_path
        message_canverter = canvtr.CANverter(message_dbc_file_path)

def data_file_btn_callback(event):
    global log_file_path
    log_file_path = askopenfilename(title = "Select Data File",filetypes = (("Data Files","*.log"),("all files","*.*"))) 
    if log_file_input_text != '':
        log_file_input_text.value = log_file_path
    
def create_project_button_callback(event):
    global time_series_canverter
    global message_canverter
    global log_file_path 
    global time_series_dbc_file_input_text
    global message_dbc_file_input_text
    global project_name_input_text

    if len(create_project_float_panel[-1]) > 1:
        create_project_float_panel[-1].pop(1)
    create_project_float_panel[-1].append("Importing Data...")
    try:
        # Get the file extension
        log_file_path = log_file_input_text.value
        file_extension = log_file_path.split(".")[-1].lower()
        project_name = project_name_input_text.value.replace(" ", "_").lower()
        if project_name != None and project_name != '':
            if (file_extension == 'log'):
                if (time_series_canverter == None):
                    try:
                        time_series_canverter = canvtr.CANverter(time_series_dbc_file_input_text.value)
                    except Exception as ex:
                        create_project_float_panel[-1][-1]= ("Importing Failed. Please provide a valid time series .dbc file.")
                        raise ex
                if (message_canverter == None):
                    try:
                        message_canverter = canvtr.CANverter(message_dbc_file_input_text.value)
                    except Exception as ex:
                        create_project_float_panel[-1][-1]= ("Importing Failed. Please provide a valid message .dbc file.")
                        raise ex
                build_current_project(log_file_path, project_name)
                project_name_select.options = get_projects()
                project_name_input_text.value = ""
                time_series_dbc_file_input_text = ""
                message_dbc_file_input_text = ""
                project_name_input_text = ""
            else:
                create_project_float_panel[-1][-1]= ("Importing Failed. Please provide a valid .log file")
                raise Exception
            create_project_float_panel[-1][-1]= ("Importing Successful!")
    except Exception as e:
        traceback.print_exc()
        create_project_float_panel[-1][-1]= ("Importing Failed!")

def choose_csv_file_btn_callback(event):
    global csv_file_path
    csv_file_path = asksaveasfilename(title = "Save Exported CSV File", filetypes = (("CSV Files","*.csv"),("all files","*.*")))
    csv_export_text.value = csv_file_path

def save_csv_button_callback(event):
    global curr_project
    global csv_file_path
    global current_project_name
    csv_file_path = csv_export_text.value
    if len(export_project_float_panel[-1]) > 1:
        export_project_float_panel[-1].pop(1)
    export_project_float_panel[-1].append("Exporting Data...")
    try:
        if interpolate_csv_btn.value:
            curr_project.ts_dataframe.to_csv(csv_file_path)
        else:
            pd.read_pickle("./PROJECTS/"+current_project_name+".project").to_csv(csv_file_path)
        csv_file_path = ''
        export_project_float_panel[-1][-1]= ("Export Successful!")
    except:
        export_project_float_panel[-1][-1]= ("Export Failed!")
        
def export_data_panel_btn_callback(event):
    csv_export_text.placeholder = USER_ROOT_PATH
    update_float_display(float_panel_display, pn.layout.FloatPanel(export_project_float_panel, name='Export to CSV', height=300, width=500, contained=False, position="center", theme="#00693e"))
    if len(export_project_float_panel[-1]) > 1:
        export_project_float_panel[-1].pop(1)
    
def create_new_project_float_btn_callback(event):
    update_float_display(float_panel_display, pn.layout.FloatPanel(create_project_float_panel, name='Create Project', height=440, contained=False, position="center", theme="#00693e"))
    project_name_input_text.placeholder = "Project Name..."
    time_series_dbc_file_input_text.placeholder = USER_ROOT_PATH
    log_file_input_text.placeholder = USER_ROOT_PATH
    if len(create_project_float_panel[-1]) > 1:
        create_project_float_panel[-1].pop(1)
    update_message_log()

####################################################
def favorites_save_btn_callback(event):
    if len(save_groupings_float_panel[-1]) > 1:
        save_groupings_float_panel[-1].pop(1)
    update_float_display(float_panel_display, pn.layout.FloatPanel(save_groupings_float_panel, name='Save Signal Grouping', height=200, width=500, contained=False, position="center", theme="#00693e"))

def favorites_del_btn_callback(event):
    if len(delete_groupings_float_panel[-1]) > 1:
        delete_groupings_float_panel[-1].pop(1)
    update_float_display(float_panel_display, pn.layout.FloatPanel(delete_groupings_float_panel, name='Save Signal Grouping', height=200, width=500, contained=False, position="center", theme="#00693e"))

def group_save_float_btn_callback(event):
    global favorites_select
    signals = y_axes_field_multiselect.value

    if len(save_groupings_float_panel[-1]) > 1:
        save_groupings_float_panel[-1].pop(1)
    save_groupings_float_panel[-1].append("Saving Data...")

    if not os.path.exists('FAVORITES'):
        os.makedirs('FAVORITES')
    
    try:
        with open('./FAVORITES/'+ group_name.value + '.pkl','wb') as f:
            pickle.dump(signals,f)
        save_groupings_float_panel[-1][-1] = ('Saving Successful!')
    except:
        save_groupings_float_panel[-1][-1] = ('Saving Failed!')

    favorites_select.options = get_favorites()
    favorites_delete.options = get_favorites()

def delete_grouping_float_btn_callback(event):
    global favorites_select
    
    if len(delete_groupings_float_panel[-1]) > 1:
        delete_groupings_float_panel[-1].pop(1)
    delete_groupings_float_panel[-1].append("Deleting Data...")

    try:
        os.remove('./FAVORITES/' + favorites_delete.value + '.pkl')
        delete_groupings_float_panel[-1][-1] = ('Deleting Successful!')
    except:
        delete_groupings_float_panel[-1][-1] = ('Deleting Failed!')

    favorites_select.options = get_favorites() #Update dropdown menu
    favorites_delete.options = get_favorites()

### Message Log
json_css = '''
.json-formatter-constructor-name {
    color: LightGray !important;
}
.json-formatter-key {
    color: black !important;
}
.json-formatter-number {
    color: #00693e !important;
}
'''

msg_json = pn.pane.JSON({'No messages':''}, name='message log', sizing_mode='stretch_width', theme='light') #, hover_preview=True)

pn.config.raw_css.append(json_css)

def update_message_log():
    global msg_json
    global curr_project
    msg_json.object = curr_project.msg_dict
def clear_all_columns_btn_callback(event):
    y_axes_field_multiselect.value = []

def generate_plot_btn_callback(event):
    global curr_project
    plotly_pane.object = update_graph_figure(curr_project.ts_dataframe, y_axes_field_multiselect.value, x_axis_field_select.value, comb_axes_switch.value)
    final_filter = y_axes_field_multiselect.value.copy()
    final_filter.insert(0, TIME_FIELD)
    update_tabulator_display(tabulator_display, pn.widgets.Tabulator(curr_project.ts_dataframe[final_filter], show_index = False, page_size=10, layout='fit_columns', sizing_mode='stretch_width'))

"""
############################ SIDEBAR COMPONENTS ##################################
"""
project_name_select = pn.widgets.Select(name='Select Project',options=project_options, align="center")
@pn.depends(project_name_select.param.value, watch=True)
def update_project(project_name_select):
    """
    On-change function for project name select
    """
    global curr_project, current_project_name
    y_axes_field_multiselect.name = "Y axes fields for "+project_name_select
    x_axis_field_select.name = "X axis field for "+project_name_select
    y_axes_field_multiselect.value = []
    x_axis_field_select.value = TIME_FIELD
    with open("./PROJECTS/"+project_name_select+".project", 'rb') as project:
        curr_project = pickle.load(project)
        
    interpolate_dataframe()
    current_project_name = project_name_select

favorites_select = pn.widgets.Select(name='Signal Groupings',options=favorites_options)
@pn.depends(favorites_select.param.value, watch=True)
def favorites_load(favorites_select):
    """
    On-change function for favorites select
    """
    with open('./FAVORITES/'+ favorites_select + '.pkl','rb') as f:
        y_axes_field_multiselect.value = pickle.load(f)
        
clear_all_columns_btn = create_button(clear_all_columns_btn_callback, 'Clear all columns', SIDEBAR_BUTTON_HEIGHT, SIDEBAR_ROW_HEIGHT)
generate_plot_btn = create_button(generate_plot_btn_callback, 'Generate plot', SIDEBAR_BUTTON_HEIGHT, SIDEBAR_ROW_HEIGHT)
create_project_button = create_button(create_project_button_callback, 'Create Project', SIDEBAR_BUTTON_HEIGHT, SIDEBAR_ROW_HEIGHT)
create_new_project_float_btn = create_button(create_new_project_float_btn_callback, 'Create Project',  SIDEBAR_BUTTON_HEIGHT, SIDEBAR_ROW_HEIGHT)
export_data_panel_btn = create_button(export_data_panel_btn_callback, 'Export Project', SIDEBAR_BUTTON_HEIGHT, SIDEBAR_ROW_HEIGHT)
comb_axes_switch_name = pn.widgets.StaticText(name='Combine Y-Axes', value='')
combine_axes_tooltip = pn.widgets.TooltipIcon(value="Click the \"Generate plot\" button below to implement changes", width=20)
y_axes_field_multiselect = pn.widgets.MultiChoice(name="Y Variables for "+project_name_select.value, value=[],options=[], align="center")
x_axis_field_select = pn.widgets.Select(name="X Variable for "+project_name_select.value,options=[])
favorites_save_btn = create_button(favorites_save_btn_callback, 'Save Grouping', SIDEBAR_BUTTON_HEIGHT, SIDEBAR_ROW_HEIGHT)
favorites_del_btn = create_button(favorites_del_btn_callback, 'Delete Grouping', SIDEBAR_BUTTON_HEIGHT, SIDEBAR_ROW_HEIGHT)
comb_axes_switch = pn.widgets.Switch(name='Switch')

main_sidebar = pn.Column(
    pn.Row(create_new_project_float_btn, export_data_panel_btn, height=SIDEBAR_ROW_HEIGHT),
    pn.Row(project_name_select, height=SIDEBAR_ROW_HEIGHT),
    pn.Tabs(("Manual",
                pn.Column(
                    pn.Row(generate_plot_btn, clear_all_columns_btn, height = SIDEBAR_ROW_HEIGHT),
                    pn.Row(favorites_select,  height = SIDEBAR_ROW_HEIGHT),
                    pn.Row(favorites_save_btn, favorites_del_btn, height = SIDEBAR_ROW_HEIGHT),
                    pn.Row(comb_axes_switch_name, combine_axes_tooltip, comb_axes_switch, height = SIDEBAR_ROW_HEIGHT),
                    pn.Row(x_axis_field_select, height = SIDEBAR_ROW_HEIGHT),
                    pn.Row(y_axes_field_multiselect, height = SIDEBAR_ROW_HEIGHT),
                )
            ),
            ( "Groupings",
                pn.Column(
                    pn.Row(favorites_select, height = SIDEBAR_ROW_HEIGHT),
                    pn.Row(favorites_save_btn, favorites_del_btn, height = SIDEBAR_ROW_HEIGHT),
                ),
            )
    )
)

"""
############################ FLOAT COMPONENTS ################################### 
"""
#Delete Grouping Float Panel Components
delete_grouping_float_btn = create_button(delete_grouping_float_btn_callback, 'Delete', FLOAT_PANEL_BUTTON_HEIGHT)
favorites_delete = pn.widgets.Select(name='Signal Groupings', options=favorites_options, )

#Save Grouping Float Panel Components
group_save_float_btn = create_button(group_save_float_btn_callback, 'Save', FLOAT_PANEL_BUTTON_HEIGHT)
group_name = pn.widgets.TextInput(name='', placeholder='Enter a name here...')

#Create New Project Float Panel Components
time_series_dbc_file_btn = create_button(time_series_dbc_file_btn_callback, 'Upload .dbc file',  FLOAT_PANEL_BUTTON_HEIGHT, FLOAT_PANEL_ROW_HEIGHT)
message_dbc_file_btn = create_button(message_dbc_file_btn_callback, 'Upload .dbc file',  FLOAT_PANEL_BUTTON_HEIGHT, FLOAT_PANEL_ROW_HEIGHT)
data_file_btn = create_button(data_file_btn_callback, 'Upload .log file',  FLOAT_PANEL_BUTTON_HEIGHT, FLOAT_PANEL_ROW_HEIGHT)
time_series_dbc_file_input_text = pn.widgets.TextInput(name="Time series .dbc file", placeholder=USER_ROOT_PATH, height = FLOAT_PANEL_TEXT_INPUT_HEIGHT, align='center')
message_dbc_file_input_text = pn.widgets.TextInput(name="Messages .dbc file", placeholder=USER_ROOT_PATH, height = FLOAT_PANEL_TEXT_INPUT_HEIGHT, align='center')
log_file_input_text = pn.widgets.TextInput(name="CAN data .log file", placeholder=USER_ROOT_PATH, height = FLOAT_PANEL_TEXT_INPUT_HEIGHT, align='center')
project_name_input_text = pn.widgets.TextInput(name="Project Name", placeholder = "Project Name...", height=FLOAT_PANEL_TEXT_INPUT_HEIGHT, align='center')

#Export Project Float Panel Components
csv_export_text = pn.widgets.TextInput(name="Choose output directory", placeholder=USER_ROOT_PATH, height = FLOAT_PANEL_TEXT_INPUT_HEIGHT, align='center')
choose_csv_file_btn = create_button(choose_csv_file_btn_callback, 'Create .csv', FLOAT_PANEL_BUTTON_HEIGHT, FLOAT_PANEL_ROW_HEIGHT)
save_csv_button = create_button(save_csv_button_callback, 'Save', FLOAT_PANEL_BUTTON_HEIGHT, FLOAT_PANEL_ROW_HEIGHT)
interpolate_csv_btn = pn.widgets.Checkbox(name='Interpolate Data')

#Delete Groupings Float Panel
delete_groupings_float_panel = pn.Column(
    pn.Row("Select a signal grouping to delete:", height=FLOAT_PANEL_TEXT_ROW_HEIGHT),
    pn.Row(favorites_delete, height = FLOAT_PANEL_ROW_HEIGHT),
    pn.Row(delete_grouping_float_btn, height = FLOAT_PANEL_ROW_HEIGHT)
)

#Save Groupings Float Panel
save_groupings_float_panel = pn.Column(
    pn.Row("Name your signal grouping. Be sure to use _ for spaces between words:", height=FLOAT_PANEL_TEXT_ROW_HEIGHT),
    pn.Row(group_name, height = FLOAT_PANEL_ROW_HEIGHT),
    pn.Row(group_save_float_btn, height = FLOAT_PANEL_ROW_HEIGHT)
)

#Create Project Float Panel
create_project_float_panel = pn.Column(
    pn.Row("Name your project, select .log file, and .dbc file", height=FLOAT_PANEL_TEXT_ROW_HEIGHT),
    pn.Row(project_name_input_text, height = FLOAT_PANEL_ROW_HEIGHT),
    pn.Row(time_series_dbc_file_input_text, time_series_dbc_file_btn, height = FLOAT_PANEL_ROW_HEIGHT),
    pn.Row(message_dbc_file_input_text, message_dbc_file_btn, height = FLOAT_PANEL_ROW_HEIGHT,),
    pn.Row(log_file_input_text, data_file_btn, height = FLOAT_PANEL_ROW_HEIGHT),
    pn.Row(create_project_button, height = FLOAT_PANEL_ROW_HEIGHT),
) 

#Export Project Float Panel
export_project_float_panel = pn.Column(
    pn.Row("Select the project you want to export into a .csv", height=FLOAT_PANEL_TEXT_ROW_HEIGHT),
    pn.Row(project_name_select, height = FLOAT_PANEL_ROW_HEIGHT),
    pn.Row(csv_export_text, choose_csv_file_btn, height = FLOAT_PANEL_ROW_HEIGHT),
    pn.Row(interpolate_csv_btn, height = FLOAT_PANEL_CHECKBOX_ROW_HEIGHT),
    pn.Row(save_csv_button, height = FLOAT_PANEL_ROW_HEIGHT)
)

"""
############################ MAIN COMPONENTS ##################################
"""
figure = update_graph_figure(curr_project.ts_dataframe, y_axes_field_multiselect.value, x_axis_field_select.value, comb_axes_switch.value)
plotly_pane = pn.pane.Plotly(figure, sizing_mode="stretch_both")
plot_display = pn.Row(plotly_pane, min_height=600, sizing_mode="stretch_both")
tabulator_display = EMPTY_TABULATOR_DISPLAY
float_panel_display = EMPTY_FLOAT_PANEL_DISPLAY

template = pn.template.FastListTemplate(
    title="Dartmouth Formula Racing",
    logo=f"data:image/jpeg;base64,{LOGO_ENCODED_STRING}",
    accent="#00693e",
    sidebar=main_sidebar,
    shadow=False
)

template.main.append(pn.Tabs(
    ("Visualize Projects", 
        pn.Column(
            plot_display,
            tabulator_display,
            float_panel_display
            )
        ), 
    ("Real-Time Plotting", 
        pn.WidgetBox(

        )
    ),
        ("Message Log", 
            pn.Column(
                msg_json
            )
        )
    ))

template.servable()
