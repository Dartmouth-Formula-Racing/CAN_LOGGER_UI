import pandas as pd
from pprint import pprint

class Project():

    def __init__(self, ts_dataframe, msg_dataframe):
        self.ts_dataframe = ts_dataframe
        self.msg_dataframe = msg_dataframe
        self.msg_dict = self.msg_dataframe.to_dict(orient='index')