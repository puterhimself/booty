"""
1. add results pickle
2. integrate with main API
"""

import math
import os
import sys
import numpy as np
import pandas as pd
from backtesting import lib
from datetime import date, datetime
from userdata.strategies.MA import MA
from backtesting import Backtest, Strategy


class simps(Strategy):
    
    minimal_roi = {'0', 1}
    sl = -0.05
        
    def init(self): pass

    def next(self):
        now: datetime = self.data.index[-1]
        if self.data.Buy == 1:
            sl = self.data.Close
            sl += (self.data.Close * self.sl)
            self.bracketorder = self.buy(size=1, sl=sl)
        
        if self.data.Sell == 1:
            sl = self.data.Close
            sl -= (self.data.Close * self.sl)
            self.bracketorder = self.sell(size=1, sl=sl)
        
        for trade in self.trades:
            trade_dur = int(now.timestamp() - trade.entry_time.timestamp()) // 60
            roi = list(filter(lambda x: int(x) <= trade_dur, self.minimal_roi.keys()))
            roi = max(roi)
            roi = self.minimal_roi[roi]
            
            if trade.pl_pct >= roi:
                trade.close()


class satish():

    def __init__(self, dataname: str=None, precursor: MA=None, config: dict=None) -> None:
        
        self.basedf = self.getdata(dataname)
        self.p = precursor
        self.config = dict(
            strategy=simps,
            cash=1000000, 
            commission=0.004, 
            trade_on_close=True,
            margin=0.008,
            exclusive_orders=False) if config is None else config
    

    def getdata(self, dataname) -> pd.DataFrame:

        _cols = ["datetime", "Open", "High", "Low", "Close", "Volume", "Closetime", \
            "Quoteassetvolume", "Trades", "BaseTBAV", "QuoteTBAV", "Ignore", ]
        df: pd.DataFrame = pd.read_csv(dataname, names=_cols, header=None)
        
        _cols = ["datetime", "Open", "High", "Low", "Close", "Volume", "Trades"]
        df = df[_cols]

        df['datetime'] = pd.to_datetime(df['datetime'], unit='ms', utc=True)
        df['datetime'] = df['datetime'].dt.tz_convert('Asia/Kolkata')
        df.set_index('datetime', drop=True, inplace=True)

        return df

    
    def df(self, dataname):
        df = self.getdata(dataname)
        self.basedf = df.copy()
        del df
   

    def mod(self, df: pd.DataFrame, p: MA) -> pd.DataFrame:
    
        df = df.resample(p.timeframe).apply(lib.OHLCV_AGG)
        df.columns = [i.lower() for i in df.columns]
        df = p.populate_indicators(self, dataframe=df, metadata={})
        df = p.populate_buy_trend(self, dataframe=df, metadata={})
        df = p.populate_sell_trend(self, dataframe=df, metadata={})

        return df
    

    def prep(self, df=None, p=None):
        df = self.basedf if df is None else df
        stratdf = self.mod(df, p)
        stratdf.columns = [i.capitalize() for i in stratdf.columns]
        
        _cols = ["Open", "High", "Low", "Close", "Volume", 'Buy', 'Sell']
        stratdf = stratdf[_cols].fillna(0)

        simps.sl = p.stoploss
        simps.minimal_roi = p.minimal_roi
        return stratdf

    
    def run(self):
        data = self.prep(self.basedf, self.p)
        data = self.datablock(dict(dti=True, case='T', mods=self.mod))
        self.bt = Backtest(data=data, **self.config)
        self.results = self.bt.run()
        return self.results
    
    
    def runthis(self, data, strat, conf):

        self.config['data'] = self.prep(self.basedf, self.p)
        self.bt = Backtest(**self.config)
        self.results = self.bt.run()
        return self.results
    

    def plot(self):
        if self.results:
            self.bt.plot(resample='1D')


def run():
    stat = satish(dataname='./userData/data/BTCUSDT.csv', precursor= MA)
    res = stat.run()
    print(res)


if __name__ == "__main__":
    run()