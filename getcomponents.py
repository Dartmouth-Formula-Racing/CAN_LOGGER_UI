import panel as pn
import plotly.graph_objects as go
from constants import *
import os
from bokeh.plotting import figure as bokeh_figure
from bokeh.plotting import curdoc
from bokeh.driving import linear
import threading
import traceback

pn.extension('plotly')
pn.extension('tabulator')
pn.extension('floatpanel')



################        REAL TIME HELPERS      #####################
update_callback_remove = None
real_time_plot_figure = bokeh_figure( sizing_mode="stretch_width")

def get_tty_ports():
    tty_ports = os.listdir("/dev")
    tty_ports = list(filter(lambda port: port.startswith("tty."), tty_ports))
    return ["/dev/" + tty_port for tty_port in tty_ports]

def format_byte_message(message):
    formatted_msg = message.decode("utf-8")[:-1]
    return formatted_msg
    
################        COMPONENT CREATION HELPERS      #####################
def create_button(buttonCallback, name, height, rowHeight=None, disabled=False):
    newButton = pn.widgets.Button(name=name, align="center",height=height, disabled=disabled)
    if rowHeight != None:
        verticalMargin = (int)((rowHeight-height)/2)
        newButton.margin = (verticalMargin, verticalMargin)
    newButton.on_click(buttonCallback)
    return newButton

def create_float_panel(object, name, height, width=DEFAULT_FLOAT_PANEL_WIDTH):
    return pn.layout.FloatPanel(object, name=name, height=height, width = DEFAULT_FLOAT_PANEL_WIDTH, contained=False, position="center", theme=UI_THEME_COLOR)

def get_favorites():
    if not os.path.exists(FAVORITES_DIRECTORY_STRING):
        os.makedirs(FAVORITES_DIRECTORY_STRING)
    fav_list = [fav.split(".")[0] for fav in os.listdir(FAVORITES_DIRECTORY_STRING)]
    if '' not in fav_list:
        fav_list.insert(0,'')
    return (fav_list)

def get_projects():
    return [proj.split(".")[0] for proj in os.listdir(PROJECTS_DIRECTORY_STRING)]

################     TABULATOR DISPLAY FUNCTIONS        #####################
def update_tabulator_display(tabulatorDisplay, tabulator):
    if len(tabulatorDisplay) > 0:
        tabulatorDisplay.pop(0)
        
    if tabulator == None:
        return tabulatorDisplay
    else:
        tabulatorDisplay.append(tabulator)
        tabulatorDisplay.visible = True
        return tabulatorDisplay


################      FLOAT PANEL DISPLAY FUNCTIONS        #####################
def update_float_display(floatDisplay, floatPanel):
    if len(floatDisplay) > 0:
        floatDisplay.pop(0)
        
    if floatPanel == None:
        return floatDisplay
    else:
        floatDisplay.append(floatPanel)
        return floatDisplay
    
################      GRAPH DISPLAY FUNCTIONS        #####################
def update_graph_figure(current_dataframe, current_non_ts_dataframe, yAxesFields, xAxisField, combineAxes, scatterplot):

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


    if len(yAxesFields) == 0:
        return fig

    if combineAxes:
        grouped_plots = {}
        y_labels = []
        for column_name in yAxesFields:
            units = column_name.split('(', 1)[1].split(')', 1)[0].strip()

            in_front = column_name.split('(')[0].split()[-1].strip()
            y_label = f"{in_front} ({units})"
            
            if y_label not in y_labels:
                y_labels.append(y_label)

            if units in grouped_plots:
                grouped_plots[units].append(column_name)
            else:
                grouped_plots[units] = [column_name] 
        
        yAxesFields = y_labels
        signal_num = len(grouped_plots)

        if (signal_num > 4):
            pn.state.notifications.error("Four Y-Axes Max Limit Exceeded!", duration=YAXIS_ERROR_NOTIFICATION_MILLISECOND_DURATION)
            return fig
        
        i=1
        for units in grouped_plots:
            for column_name in grouped_plots[units]:
                if scatterplot:
                    fig.add_trace(go.Scatter(
                        x=current_non_ts_dataframe[xAxisField],
                        y=current_non_ts_dataframe[column_name],
                        name=column_name,
                        mode='markers',
                        marker=dict(size=4),
                        yaxis=f"y{i}"
                    )) 
                else:
                    fig.add_trace(go.Scatter(
                            x=current_dataframe[xAxisField],
                            y=current_dataframe[column_name],
                            name=column_name,
                            yaxis=f"y{i}"
                        )) 
                
            i=i+1   
        

    else:
        signal_num = len(yAxesFields)

        if (signal_num > 4):
            pn.state.notifications.error("Four Y-Axes Max Limit Exceeded!", duration=YAXIS_ERROR_NOTIFICATION_MILLISECOND_DURATION)
            return fig
        
        i=1
        for column_name in yAxesFields:            
            if scatterplot:
                fig.add_trace(go.Scatter(
                    x=current_non_ts_dataframe[xAxisField],
                    y=current_non_ts_dataframe[column_name],
                    name=column_name,
                    mode='markers',
                    marker=dict(size=4),
                    yaxis=f"y{i}"
                )) 
            else:
                fig.add_trace(go.Scatter(
                        x=current_dataframe[xAxisField],
                        y=current_dataframe[column_name],
                        name=column_name,
                        yaxis=f"y{i}"
                    )) 
            i=i+1
    
    fig.update_layout(
        xaxis=dict(domain=[0.2, 0.8], title=xAxisField),
    )

    fig.update_layout(
        yaxis1=dict(
            title=yAxesFields[0],
        ),   
    )

    if signal_num >= 2:
        fig.update_layout(
            yaxis2=dict(
                title=yAxesFields[1],
                overlaying="y",
                side="right",
            ),   
        )
    
    
    if signal_num >= 3:
        fig.update_layout(
            yaxis3=dict(
                title=yAxesFields[2],
                anchor="free", 
                overlaying="y", 
                autoshift=True,
            ),   
        )
    
    if signal_num >= 4:
        fig.update_layout(
            yaxis4=dict(
                title=yAxesFields[3],
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