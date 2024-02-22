import panel as pn
import base64
import os

TIME_FIELD = 'Time (ms)'
EMPTY_FLOAT_PANEL_DISPLAY = pn.Row(visible = False, height = 0, width = 0)
EMPTY_TABULATOR_DISPLAY = pn.Row(visible=False, sizing_mode="stretch_both")
FLOAT_PANEL_BUTTON_HEIGHT = 35
FLOAT_PANEL_ROW_HEIGHT = 70
FLOAT_PANEL_TEXT_INPUT_HEIGHT = 70
FLOAT_PANEL_CHECKBOX_ROW_HEIGHT = 15
FLOAT_PANEL_TEXT_ROW_HEIGHT = 60

SIDEBAR_BUTTON_HEIGHT = 35
SIDEBAR_ROW_HEIGHT = 70
USER_ROOT_PATH = os.path.expanduser("~")

with open("DFRLOGO.png","rb") as image_file:
    LOGO_ENCODED_STRING = base64.b64encode(image_file.read()).decode("utf-8")

