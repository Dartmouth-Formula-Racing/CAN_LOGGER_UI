import datetime

import panel as pn
import numpy as np
import pandas as pd
from random import randint
import plotly.express as px

from functools import partial

pn.extension(sizing_mode="stretch_both")
pn.extension('plotly')

ACCENT_BASE_COLOR = "#00693e"

df = pd.DataFrame(columns=["Time", "Value"])
streaming_component = px.line(data_frame=df)
panel = pn.pane.Plotly(streaming_component)

def update(source):
    time = datetime.datetime.utcnow()
    val = randint(0,100)
    new = [time, val]
    new = pd.DataFrame(columns = source.columns, data = [new])
    source = pd.concat([source, new], axis = 0)
    print(source)

pn.state.add_periodic_callback(callback=partial(update, df), period=50)

template = pn.template.FastListTemplate(
    site="DFR GUI",
    title="Streaming using periodic callback",
    header_background=ACCENT_BASE_COLOR,
    accent_base_color=ACCENT_BASE_COLOR,
    main=[panel],
).servable()