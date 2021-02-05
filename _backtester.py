from datetime import datetime
import pyfolio as pf
import pandas as pd


from datahandler import dataHandler
from userData.strategies.MA import MA

import backtrader as bt
from backtrader.feed import DataBase
from backtrader import date2num, TimeFrame, Strategy
from backtrader.utils.py3 import filter, string_types, integer_types
from backtrader.analyzers import (SQN, AnnualReturn, TimeReturn, SharpeRatio,
                                  TradeAnalyzer)


# OpenTime,Open,High,Low,Close,Volume,CloseTime,QuoteAssetVolume,NumberOfTrades,BaseTBAV,QuoteTBAV,Ignore


class model(DataBase):
    
    lines = ('trades',)
    params = (
        ('datetime', 0),
        ('open', 1),
        ('high', 2),
        ('low', 3),
        ('close', 4),
        ('volume', 5),
        ('tardes', 6),
        ('openinterest', -1),
    )

    datafields = ["datetime", "open", "high", "low", "close", "volume", "trades"]

    def __init__(self, precursor) -> None:
        super().__init__()        
        self._cols = ["datetime", "open", "high", "low", "close", "volume", "trades"]
        self.precursor = precursor
        self.df = self.p.dataname


    def start(self):
        self.df = self.df[self._cols]

        # self.df["dt"] = self.df["datetime"]
        # self.df["dt"] = pd.to_datetime(self.df["datetime"], unit="ms")
        # aggvars = {
        #     "datetime": "first",
        #     "open": "first",
        #     "high": "max",
        #     "low": "min",
        #     "close": "last",
        #     "volume": "sum",
        #     "trades": "sum",
        #     # "dt": "first"
        # }
        # self.df = datahandler.Grouper(self.df, freq=precursor.timeframe, key="datetime", aggVars=aggvars)

        self.df = self.precursor.populate_indicators(self.df)
        self.df = self.precursor.populate_buy_trend(self.df)
        self.df = self.precursor.populate_sell_trend(self.df)
        self._cols = self.df.columns

        model.params = {cols:self._cols.get_loc(cols) for cols in self._cols}
        model.params["openinterest"] = -1
        model.params["name"] = "BTCUSD"
        model.params["timeframe"] = TimeFrame.Minutes
        model.params["compression"] = 5
        model.params["nullvalue"] = 0.0

        model.lines = (i for i in self._cols if i not in self.getlinealiases())

        super().start()
        self._rows = self.df.itertuples()

    def _load(self):
        try:
            row = next(self._rows)
        except StopIteration:
            return False

        for datafield in self.getlinealiases():  # for default cols
            if datafield == "datetime":
                continue

            colidx = getattr(self.params, datafield)
            if colidx < 0:
                continue
            
            # if datafield in self.params:
            getattr(self.lines, datafield)[0] = row[colidx]
            

        for datafield in self._cols:  # for custom cols
            if datafield in self.getlinealiases():
                continue

            # colidx = getattr(self.params, datafield)
            getattr(self.lines, datafield)[0] = row[datafield]

        colidx = self.params.get("datetime")
        tstamp = row[colidx]

        dt = tstamp.to_pydatetime()
        dtnum = date2num(dt)

        line = getattr(self.lines, "datetime")
        line[0] = dtnum

        return True


class strat(Strategy):
       

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            self.log('ORDER ACCEPTED/SUBMITTED', dt=order.created.dt)
            self.order = order
            return

        if order.status in [order.Expired]:
            self.log('BUY EXPIRED')

        elif order.status in [order.Completed]:
            if order.isbuy():
                print(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

            else:  # Sell
                print('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))


    def next(self):
        if not self.position:

            if self.data.buy == 1:
                entry = self.data.close
                sl = entry - (entry * 0.0014)
                tp = entry + (entry * 0.0018)

                self.bracketorder = self.buy_bracket(
                    data=self.data, size=0.01,
                    stopprice=sl, stopexec=bt.Order.Stop,
                    limitprice=tp, limitexec=bt.Order.Stop)
                
                self.order = self.bracketorder[0]
            
            if self.data.sell == 1:
                entry = self.data.close
                sl = entry + (entry * 0.0014)
                tp = entry - (entry * 0.0018)

                self.bracketorder = self.sell_bracket(
                    data=self.data, size=0.01,
                    stopprice=sl, stopexec=bt.Order.Stop,
                    limitprice=tp, limitexec=bt.Order.Stop)
                
                self.order = self.bracketorder[0]
        else:
            #5 minutes timer exit
            if self.order.executed:
                entryTime = self.order.executed.dt
                if (entryTime + pd.Timedelta(value=5, unit='min')) >= entryTime:
                    self.close(size=0.01)


def getdata(df, precursor):
    _cols = ["datetime", "open", "high", "low", "close", "volume", "trades"]
    df = df[_cols]
    df['datetime'] = (df['datetime'] / 1000).astype(float)
    # df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')

    df = precursor.populate_indicators(df)
    df = precursor.populate_buy_trend(df)
    df = precursor.populate_sell_trend(df)
    print(df.head())
    _cols = df.columns
    
    params = {cols:_cols.get_loc(cols) for cols in _cols}
    params["openinterest"] = -1
    params["name"] = "BTCUSD"
    params["timeframe"] = TimeFrame.Minutes
    params["compression"] = 5
    params["nullvalue"] = 0.0
    
    lines = ["datetime", "open", "high", "low", "close", "volume"]
    lines = (i for i in _cols if i not in lines)

    class model(bt.feeds.PandasDirectData):
        nonlocal params, lines
        params = params
        lines = lines
        def _load(self):
            try:
                row = next(self._rows)
                print(row)
            except StopIteration:
                return False

            for datafield in self.getlinealiases():  # for default cols
                colidx = getattr(self.params, datafield)
                if colidx < 0:
                    continue
                
                getattr(self.lines, datafield)[0] = row[colidx]
    
    return model(dataname=df)


def runstrat():

    dataname='./userData/data/BTCUSDT.csv'
    _cols = [
            "datetime",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "closetime",
            "QuoteAssetVolume",
            "trades",
            "BaseTBAV",
            "QuoteTBAV",
            "Ignore",
        ]
    df = pd.read_csv(dataname, names=_cols)
    data = getdata(df, MA)
    bro = bt.Cerebro()
    
    bro.broker.set_coc(True)
    bro.broker.setcommission(commission=0.04)
    
    bro.adddata(data)
    bro.addstrategy(strat)
    bro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')
    bro.addanalyzer(SQN)
    # bro.addanalyzer(AnnualReturn)
    # bro.addanalyzer(SharpeRatio, legacyannual=True)
    bro.addanalyzer(TradeAnalyzer)
    bro.addwriter(bt.WriterFile, csv=True, rounding=4)
    backtest = bro.run()

    # bro.plot(plot=True)
    # pyfoliozer = backtest[0]
    # pyfoliozer = pyfoliozer.analyzers.getbyname('pyfolio')
    
    # returns, positions, transactions, gross_lev = pyfoliozer.get_pf_items()
    # print(returns)
    # pf.create_full_tear_sheet(
    #     returns,
    #     positions=positions,
    #     transactions=transactions,
    #     gross_lev=gross_lev,
    #     live_start_date='2005-05-01',
    #     round_trips=True)
    return backtest

if __name__ == "__main__":
    analysis = runstrat()