import panel as pn
import plotly.graph_objects as go
from constants import *
import os

pn.extension('plotly')
pn.extension('floatpanel')
pn.extension('tabulator')


################        COMPONENT CREATION HELPERS      #####################
def create_button(buttonCallback, name, height, rowHeight=None):
    newButton = pn.widgets.Button(name=name, align="center",height=height)
    if rowHeight != None:
        verticalMargin = (int)((rowHeight-height)/2)
        newButton.margin = (verticalMargin, verticalMargin)
    newButton.on_click(buttonCallback)
    return newButton

def get_favorites():
    return [fav.split(".")[0] for fav in os.listdir("./FAVORITES/")]

def get_projects():
    return [proj.split(".")[0] for proj in os.listdir("./PROJECTS/")]

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
def update_graph_figure(current_dataframe, yAxesFields, xAxisField, combineAxes):
    # df: csv data dataframe
    # y: list of attributes from csv we want to graph (dataframe headers)

    # Only handles up to 4...    
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

        i=1
        for units in grouped_plots:
            for column_name in grouped_plots[units]:
                fig.add_trace(go.Scatter(
                    x=current_dataframe[xAxisField],
                    y=current_dataframe[column_name],
                    name=column_name,
                    yaxis=f"y{i}"
                )) 
            i=i+1   
        signal_num = len(grouped_plots)

    else:
        i=1
        for column_name in yAxesFields:
            fig.add_trace(go.Scatter(
                x=current_dataframe[xAxisField],
                y=current_dataframe[column_name],
                name=column_name,
                yaxis=f"y{i}"
            ))
            i=i+1
        signal_num = len(yAxesFields)
    
    fig.update_layout(
        xaxis=dict(domain=[0.2, 0.8], title=xAxisField),
    )

    signal_num = len(yAxesFields)

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