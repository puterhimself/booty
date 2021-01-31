import schedule
import pandas as pd
from threading import Thread
from data.databox import databox
import data





class processor():

    def __init__(self, df) -> None:
        self.theBox: databox = df

    def logicalize(self, box: databox):
        box.squeeze()

        for name, st in box.Strats.items():
            box.mod(name, self.apply, modclass=st)


    def undestand():
        """
        Generate alerts 
        """
        pass

    def apply(self, scrip: data.blocks, modclass):
        meta = {
            'resample': modclass.timeframe
        }
        df = scrip._df(meta).iloc[-modclass.startup_candle_count:]
        df = modclass.populate_indicators(df)
        df = modclass.populate_buy_trend(df)
        df = modclass.populate_sell_trend(df)
        df.fillna(0, inplace=True)

        return df[['buy', 'sell']].iloc[-3:]


    def run(self,):
        dataloop = Thread(target=self.df.live)
        schedule.every().minutes.do()
        schedule.every().minutes.do()
        schedule.every().minutes.do()
        schedule.every().minutes.do()

        while True:
            schedule.run_pending()

    # def getcalc
    # CONFIG WISE CALC OVER DATABLOCK
    # get LERTS check conditions
    
    # DEF SEND ALERTS