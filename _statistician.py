import math
import numpy as np
import pandas as pd
from backtesting import lib
from datetime import datetime
from userData.strategies.MA import MA
from backtesting import Backtest, Strategy


class BattleStrat(Strategy):

    def init(self):
        pass
    
    def next(self):
        if not self.position:

            if self.data.buy == 1:
                entry = self.data.Close
                sl = entry - (entry * 0.0014)
                entry = self.data.Close
                tp = entry + (entry * 0.0018)
                qty = entry * 0.01
                qty = qty / self.equity

                self.bracketorder = self.buy(size=1, sl=sl)
            
            if self.data.sell == 1:
                entry = self.data.Close
                sl = entry + (entry * 0.0014)
                tp = entry - (entry * 0.0018)
                qty = entry * 0.01
                qty = qty / self.equity

                self.bracketorder = self.sell(size=1, sl=sl)
        
        else:
            self.position.close()


def getdata(dataname='./userData/data/BTCUSDT.csv', precursor: MA= MA, resample='15min'):

    _cols = ["datetime", "Open", "High", "Low", "Close", "Volume",\
    "Closetime", "Quoteassetvolume", "Trades", "BaseTBAV", "QuoteTBAV", "Ignore", ]
    df: pd.DataFrame = pd.read_csv(dataname, names=_cols)
    
    _cols = ["datetime", "Open", "High", "Low", "Close", "Volume", "Trades"]
    df = df[_cols]

    df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
    df.set_index('datetime', drop=True, inplace=True)

    if resample is not None: df = df.resample(resample).apply(lib.OHLCV_AGG)

    if precursor is not None:
        df = precursor.populate_indicators(dataframe=df)
        df = precursor.populate_buy_trend(dataframe=df)
        df = precursor.populate_sell_trend(dataframe=df)

    return df.fillna(0)


class simps(Strategy):
    precursor = MA
    
    def init(self):

        self.p = self.precursor
        self.sl = self.p.stoploss
        self.df = self.data.df

        # self.df = self.df.resample(self.p.timeframe).apply(lib.OHLCV_AGG)
        self.df.columns = [col.lower() for col in self.df.columns]
        self.df = self.p.populate_indicators(self.df)
    
        self.longs = self.I(self.Signal, self.df, 'buy')
        self.shorts = self.I(self.Signal, self.df, 'sell')


    def next(self):
        now: datetime = self.data.index[-1]
        if self.longs == 1:
            sl = self.data.Close
            sl += (self.data.Close * self.sl)
            self.bracketorder = self.buy(size=1, sl=sl)
        
        if self.shorts == 1:
            sl = self.data.Close
            sl -= (self.data.Close * self.sl)
            self.bracketorder = self.sell(size=1, sl=sl)
        
        for trade in self.trades:
            trade_dur = int(now.timestamp() - trade.entry_time.timestamp()) // 60
            roi = list(filter(lambda x: int(x) <= trade_dur, self.p.minimal_roi.keys()))
            roi = max(roi)
            roi = self.p.minimal_roi[roi]
            pnl = 0 if math.isnan(trade.pl_pct) else trade.pl_pct
            if trade.pl_pct >= roi:
                trade.close()


    def Signal(self, data, side):
        if side is 'buy':
            longs = self.p.populate_buy_trend(data)
            return longs['buy'].fillna(0).values

        if side is 'sell':  
            shorts = self.p.populate_sell_trend(data)
            return shorts['sell'].fillna(0).values
            
        

if __name__ == "__main__":

    data = getdata(precursor=None)

    backtest = Backtest(data=data, 
    strategy=simps,
    cash=1000000, 
    commission=0.004, 
    trade_on_close=True,
    margin=0.008,
    exclusive_orders=False)

    # result = backtest.optimize(precursor=[MA])
    result = backtest.run()
    print(result)
    backtest.plot(resample='1D')