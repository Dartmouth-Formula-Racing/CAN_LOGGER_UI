import pandas as pd

class Project():

    def __init__(self, time_field):
        self.ts_dataframe = pd.DataFrame(columns=[time_field, 'y'])
        self.msg_dict = dict()

    def store_msg_df_as_dict(self, msg_df):
        self.msg_dict = msg_df.set_index('Time (ms)').to_dict()