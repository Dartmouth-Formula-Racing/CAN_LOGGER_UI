import datetime

import panel as pn
import numpy as np
import pandas as pd
from random import randint
import plotly.express as px

pn.extension(sizing_mode="stretch_both")
pn.extension('plotly')

ACCENT_BASE_COLOR = "#00693e"




df = pd.DataFrame(columns=["Time", "Value"])
streaming_component = px.line(data_frame=df)
panel = pn.pane.Plotly(streaming_component)

def update():
    time = datetime.datetime.utcnow()
    val = randint(0,100)
    print(time,val)
    newrow = {"Time":time,"Value":val}

    df = df.append(newrow)

    print(df)

pn.state.add_periodic_callback(callback=update, period=50)

template = pn.template.FastListTemplate(
    site="DFR GUI",
    title="Streaming using periodic callback",,
    header_background=ACCENT_BASE_COLOR,
    accent_base_color=ACCENT_BASE_COLOR,
    main=[panel],
).servable()