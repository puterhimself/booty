from os import name
import sys
import const as c
import pandas as pd
from data.blocks import blocks
from data.datadispenser import datadispenser


class databox(datadispenser):

    def __init__(self, scrips: list, context='live', name='theBox™') -> None:
        super().__init__()

        self.scrips = pd.Series({scrip: blocks(scrip, context) for scrip in scrips}, name=name)
        self.mods = []
    

    def __getattr__(self, name):
        try:
            # if name in self.scrips.keys():
                return self.scrips.at[name]
            # else:
            #     raise AttributeError(f'{name} Not Found:')

        except KeyError:
            msg = "'{0}' object has no attribute '{1}'"
            raise AttributeError(msg.format(type(self).__name__, name))
    

    def mapply(self, func, *args, **kwargs):
        self.scrips.apply(lambda x: getattr(x, func)(*args, **kwargs))
        

    def squeeze(self):
        self.scrips.apply(lambda scrip: scrip.squeeze())


    def mod(self, name, func, *args, **kwargs):
        self.scrips.apply(
            lambda scrip: scrip.mod(name, func(scrip, *args, **kwargs), )
        )


    def klinestream(self):
        meta = {
            'channels': ['kline_1m'],
            'stream_label': self.name,
            'stream_buffer_name': self.name,
            'output': 'dict'
        }
        streamID = self.sleeve(self.scrips.keys(), meta)
        
        while True:
            if self.ws.is_manager_stopping(): sys.exit(0) 
        
            res = self.ws.pop_stream_data_from_stream_buffer(self.name)
            if 'data' in res:
                if res['data']['x']:
                    res = res['data']['k'].values()
                    res: pd.DataFrame = pd.DataFrame.from_dict(
                        {idx: val for idx, val in zip(c._kline, res) }
                    )
                    self.scrips[res.symbol].df = res[c._B_cols_L]    