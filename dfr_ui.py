import panel as pn
import os
import pandas as pd
import CANverter as canvtr
import projects
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter import Tk
import plotly.graph_objects as go
import base64
import traceback
import copy
import pickle
import json

pn.extension('plotly')
pn.extension('floatpanel')
pn.extension('tabulator')

time_field = 'Time (ms)'
curr_project = projects.Project(time_field)
curr_project.ts_dataframe = pd.DataFrame(columns=[time_field, 'y'])
time_series_canverter = None
message_canverter = None
log_file_path = ''
csv_file_path = ''
project_options = [proj.split(".")[0] for proj in os.listdir("./PROJECTS/")]
current_project_name = ''
favorites_options = [fav.split(".")[0] for fav in os.listdir("./FAVORITES/")]
button_height = 35

Tk().withdraw()
root_path = os.path.expanduser("~")

with open("dfr.jpeg","rb") as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode("utf-8")

comb_axes_switch = pn.widgets.Switch(name='Switch')

def graphing():
    # df: csv data dataframe
    # y: list of attributes from csv we want to graph (dataframe headers)

    # Only handles up to 4...
    global curr_project
    
    ys = column_select_choice.value
    switch = comb_axes_switch.value
    x = x_select_choice.value
    fig = go.Figure()
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',    
        autosize=True
    )
    fig.update_xaxes(
        showline=True,
        linecolor='black',
        mirror=True,
        gridcolor='rgb(180, 180, 180)',
        zeroline=True,
        zerolinecolor='rgb(180, 180, 180)'
    )
    fig.update_yaxes(
        showline=True,
        linecolor='black',
        mirror=True,
        gridcolor='rgb(180, 180, 180)',
        zeroline=True,
        zerolinecolor='rgb(180, 180, 180)'
    )


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

        i=1
        for units in grouped_plots:
            for column_name in grouped_plots[units]:
                fig.add_trace(go.Scatter(
                    x=curr_project.ts_dataframe[x],
                    y=curr_project.ts_dataframe[column_name],
                    name=column_name,
                    yaxis=f"y{i}"
                )) 
            i=i+1   
        signal_num = len(grouped_plots)

    else:
        i=1
        for column_name in ys:
            fig.add_trace(go.Scatter(
                x=curr_project.ts_dataframe[x],
                y=curr_project.ts_dataframe[column_name],
                name=column_name,
                yaxis=f"y{i}"
            ))
            i=i+1
        signal_num = len(ys)
    
    fig.update_layout(
        xaxis=dict(domain=[0.2, 0.8], title=x),
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
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='left',
            x=0.1
        )
    )

    return fig

def build_current_project(log_file_path, project_name):
    global curr_project
    global time_series_canverter
    global message_canverter

    curr_project.ts_dataframe = time_series_canverter.log_to_dataframe(log_file_path)
    curr_project.ts_dataframe = curr_project.ts_dataframe.sort_values(by=time_field)
    curr_project.msg_dict = curr_project.store_msg_df_as_dict(message_canverter.log_to_dataframe(log_file_path).sort_values(by=time_field))
    with open("./PROJECTS/"+project_name+".project", 'wb') as f:
        pickle.dump(curr_project, f)

    interpolate_dataframe()
    

def interpolate_dataframe():
    global curr_project
    
    # Interpolate all columns linearly based on the "time" column

    if 'Time (s)' not in curr_project.ts_dataframe.columns:
        curr_project.ts_dataframe.insert(0, 'Time (s)', curr_project.ts_dataframe['Time (ms)'] / 1000)

    curr_project.ts_dataframe = curr_project.ts_dataframe.interpolate(method='linear', axis=0)
    all_columns = curr_project.ts_dataframe.columns.tolist()
    x_select_choice.options = all_columns

    columns_to_remove = ['Time (s)', 'Time (ms)']
    copy_current_dataframe = curr_project.ts_dataframe.drop(columns=columns_to_remove)
    y_columns = copy_current_dataframe.columns.tolist()
    column_select_choice.options = y_columns
    

def time_series_dbc_file_picker_callback(event):
    global time_series_canverter
    time_series_dbc_file_path = askopenfilename(title = "Select Time Series DBC File",filetypes = (("DBC Files","*.dbc"),("all files","*.*"))) 
    time_series_dbc_file_input_text.value = time_series_dbc_file_path
    time_series_canverter = canvtr.CANverter(time_series_dbc_file_path)

def message_dbc_file_picker_callback(event):
    global message_canverter
    message_dbc_file_path = askopenfilename(title = "Select Message DBC File",filetypes = (("DBC Files","*.dbc"),("all files","*.*"))) 
    message_dbc_file_input_text.value = message_dbc_file_path
    message_canverter = canvtr.CANverter(message_dbc_file_path)

def data_file_picker_callback(event):
    global log_file_path
    log_file_path = askopenfilename(title = "Select Data File",filetypes = (("Data Files","*.log"),("all files","*.*"))) 
    log_file_input_text.value = log_file_path
    
def import_data_callback(event):
    global time_series_canverter
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
                if (time_series_canverter == None):
                    print('Handle case later')
                else:
                    build_current_project(log_file_path, project_name)
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
    global curr_project
    global csv_file_path
    global current_project_name
    csv_file_path = csv_export_text.value
    if len(csv_export_selection[-1]) > 1:
        csv_export_selection[-1].pop(1)
    csv_export_selection[-1].append("Exporting Data...")
    try:
        if interpolate_csv_btn.value:
            curr_project.ts_dataframe.to_csv(csv_file_path)
        else:
            pd.read_pickle("./PROJECTS/"+current_project_name+".project").to_csv(csv_file_path)
        csv_file_path = ''
        csv_export_selection[-1][-1]= ("Export Successful!")
    except:
        csv_export_selection[-1][-1]= ("Export Failed!")
        
def export_data_panel(event):
    csv_export_text.placeholder = root_path
    float_panel.append(pn.layout.FloatPanel(csv_export_selection, name='Export to CSV', height=330, contained=False, position="center", theme="#00693e"))
    if len(csv_export_selection[-1]) > 1:
        csv_export_selection[-1].pop(1)
    
def import_data_panel(event):
    float_panel.append(pn.layout.FloatPanel(log_import_selection, name='Create Project', height=420, contained=False, position="center", theme="#00693e"))
    project_name_input_text.placeholder = "Project Name..."
    time_series_dbc_file_input_text.placeholder = root_path
    log_file_input_text.placeholder = root_path
    if len(log_import_selection[-1]) > 1:
        log_import_selection[-1].pop(1)

#CSV_EXPORT FUNCTION WIDGETS
csv_export_text = pn.widgets.TextInput(placeholder=root_path, height = 50, width = 300,align='center')
choose_csv_file_btn = pn.widgets.Button(name='Choose a file', height=50,align='center')
choose_csv_file_btn.on_click(csv_file_picker_callback)
save_csv_button = pn.widgets.Button(name='Save', height=50)
save_csv_button.on_click(save_csv_callback)
export_data_panel_btn = pn.widgets.Button(name='Export Project', align="center",height=35)
export_data_panel_btn.on_click(export_data_panel)
interpolate_csv_btn = pn.widgets.Checkbox(name='Interpolate Data')

# IMPORT_DATA FUNCTION WIDGETS
import_data_panel_btn = pn.widgets.Button(name='Create Project',align="center",height=35)
import_data_panel_btn.on_click(import_data_panel)
time_series_dbc_file_btn = pn.widgets.Button(name='Upload time series .dbc file', height=50)
time_series_dbc_file_btn.on_click(time_series_dbc_file_picker_callback)
message_dbc_file_btn = pn.widgets.Button(name='Upload message .dbc file', height=50)
message_dbc_file_btn.on_click(message_dbc_file_picker_callback)
data_file_btn = pn.widgets.Button(name='Upload .log file', height=50)
data_file_btn.on_click(data_file_picker_callback)
time_series_dbc_file_input_text = pn.widgets.TextInput(placeholder=root_path, height = 50)
message_dbc_file_input_text = pn.widgets.TextInput(placeholder=root_path, height = 50)
log_file_input_text = pn.widgets.TextInput(placeholder=root_path, height = 50)
project_name_input_text = pn.widgets.TextInput(name="Project Name", placeholder = "Project Name...", height=70)
import_data_button = pn.widgets.Button(name='Create Project', height=50)
import_data_button.on_click(import_data_callback)

#SELECT PROJECT FUNCTION WIDGETS
project_name_select = pn.widgets.Select(name='Select Project',options=project_options, align="center")
@pn.depends(project_name_select.param.value, watch=True)
def update_project(project_name_select):
    global curr_project
    global current_project_name
    
    column_select_choice.name = "Y Variables for "+project_name_select
    x_select_choice.name = "X Variable for "+project_name_select
    column_select_choice.value = []

    with open("./PROJECTS/"+project_name_select+".project", 'rb') as f:
        curr_project = pickle.load(f)
    
     # Interpolate all columns linearly based on the "time" column
    interpolate_dataframe()
    current_project_name = project_name_select

####################################################
def favorites_save_panel(event):
    if len(favorites_save_selection[-1]) > 1:
        favorites_save_selection[-1].pop(1)
    float_panel.append(pn.layout.FloatPanel(favorites_save_selection, name='Save Signal Grouping', height=200, width=500, contained=False, position="center", theme="#00693e"))

def favorites_del_panel(event):
    if len(favorites_del_selection[-1]) > 1:
        favorites_del_selection[-1].pop(1)
    float_panel.append(pn.layout.FloatPanel(favorites_del_selection, name='Save Signal Grouping', height=200, width=500, contained=False, position="center", theme="#00693e"))

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

### Message Log
msg_json = pn.pane.JSON(curr_project.msg_dict, name='JSON')


####################################################
  
column_select_choice = pn.widgets.MultiChoice(name="Y Variables for "+project_name_select.value, value=[],
    options=[], align="center")

x_select_choice = pn.widgets.Select(name="X Variable for "+project_name_select.value,options=[])

def clear_all_columns(event):
    column_select_choice.value = []

clear_all_columns_btn = pn.widgets.Button(name='Clear all columns', height=button_height, align="center")
clear_all_columns_btn.on_click(clear_all_columns)

def generate_plot(event):
    global curr_project
    global time_field
    try:
        final_filter = column_select_choice.value.copy()
        final_filter.insert(0, time_field)
        filtered_df = curr_project.ts_dataframe[final_filter]
        template.main[0][0][0] = pn.WidgetBox(
            pn.pane.Plotly(graphing(), sizing_mode="stretch_both", margin=10),
            pn.widgets.Tabulator(filtered_df, show_index = False, page_size=10),
            float_panel
        )
    except Exception as ex:
        raise ex

# Create an empty plot using hvplot
figure = graphing()
plotly_pane = pn.pane.Plotly(figure, sizing_mode="stretch_both", margin=10)

generate_plot_btn = pn.widgets.Button(name='Generate plot', height=button_height, align="center")
generate_plot_btn.on_click(generate_plot)
    
# Create a tabulator based on the data
tabulator_pane = pn.widgets.Tabulator(curr_project.ts_dataframe, show_index = False)
log_import_selection = pn.Column(
    "Name your project, select .log file, and .dbc file",
    pn.Row(
        project_name_input_text,
    ),
    pn.Row(
        time_series_dbc_file_input_text,
        time_series_dbc_file_btn,
    ),
    pn.Row(
        message_dbc_file_input_text,
        message_dbc_file_btn,
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
    height=80
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
        plot_generation_x,
        plot_generation_y,
        comb_axes,
        pn.Row(
            generate_plot_btn,
            clear_all_columns_btn,
        ),
    margin=(25, 10))
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

plot_display = pn.layout.Row(
    plotly_pane,
    sizing_mode="stretch_both"
)

template = pn.template.FastListTemplate(
    title="DFR CAN UI",
    logo=f"data:image/jpeg;base64,{encoded_string}",
    accent="#00693e",
    sidebar=user_input_block,
    # prevent_collision=True,
    shadow=False
)

float_panel = pn.Row(height=0, width=0,visible=False)

template.main.append(pn.Tabs(
    ("Visualize Projects", 
        pn.WidgetBox(
            plotly_pane, 
            tabulator_pane,
            float_panel
        )
    ), 
    ("Real-Time Plotting", 
        pn.WidgetBox(

        )
    ),
        ("Message Log", 
            pn.Column(
                # msg_json
            )
        )
    ))

template.servable()
