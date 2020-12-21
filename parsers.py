import sys
import time
import numpy as np
import pandas as pd
from pandas.core.frame import DataFrame
from alert import Alerts
from datetime import datetime
from conf import Configuration
from twisted.internet import reactor


class StrategyParse(Configuration):
    
    def __init__(self, Strategy, metadata):
        super().__init__()
        self.handle = dataHandler()
        self.alerts = Alerts()
        self.Strategy = Strategy
        self.metadata = metadata
        self.data = self.handle.prefetchForStrategies(metadata)
        

    def callback(self, res):
            res = self.handle.processResponse(res)
            print(res)
            if res['Is']: 
                for scrip, df in self.data.items():
                    self.data[scrip] = self.Strategy.populate_indicators(df)
                    self.data[scrip] = self.Strategy.populate_buy_trend(df)
                    self.data[scrip] = self.Strategy.populate_sell_trend(df)

                    self.alerts.stratsAlerts(scrip, df, self.bot['paisheeBot'])
            time.sleep(self.metadata['refresh'])

    def run(self): 
        self.sock.start()

class parse(Configuration):

    def __init__(self, handle):
        super().__init__()
        self.handle = handle
        self.alerts = Alerts()
        self.flag = False

        self.conns['defaultScrip'] = self.handle.klineStream(self.handle.metadata, self.sock, self.callback)
        # self.marketStream = self.handle.ws(self.sock, ['!ticker@arr'], self.callback)
    

    def run(self,):
        print('Run started')
        self.sock.start()

    
    def callback(self, res):
        try:
            if 'stream' in res:
                if res['stream'] is '!ticker@arr':
                    self.Tickers(res)

                if 'kline' in res['stream']:
                    self.Strategy(res)
                    
            
        except KeyboardInterrupt:
            self.sock.stop_socket(self.klineStream)
            self.sock.close()
            reactor.stop()
            sys.exit()
        
        # except KeyError as e:
        #     print('key not found', e)


    def Strategy(self, res):
        print('strating')
        self.handle.resDF = self.handle.processResponse(res['data'])
        if self.handle.resDF['x'].iloc[-1]: self.handle.data = self.handle.updateDF(self.handle.data, self.handle.resDF)
        time.sleep(0.05)
        print()
        for strat, meta in self.modclass.items():
            self.handle.stratDF = self.parseStrategy(self.handle.data, strat, meta)
            self.alerts.stratsAlerts(self.handle.stratDF, meta)
            self.alerts.stratHelper(self.handle.stratDF, meta)


    def parseStrategy(self, data, strat, metadata):
        stratDF = {}
        for scrip, df in data.items():
            stratDF[scrip] = df.iloc[-(3000):]
            stratDF[scrip] = self.handle.Grouper(stratDF[scrip], metadata['T']) 
            stratDF[scrip] = self.Strats[strat].populate_indicators(dataframe=df)
            stratDF[scrip] = self.Strats[strat].populate_buy_trend(dataframe=df)
            stratDF[scrip] = self.Strats[strat].populate_sell_trend(dataframe=df)
            stratDF[scrip] = self.mods(stratDF[scrip])

        return stratDF


    def parseTicker(self, metadata, res, notify=True):
        """
        parse for single 24hrTicker symbol
        """
        response = 'For {} Following has changed, Time: {}\n'.format(metadata.Symbol, datetime.fromtimestamp(metadata['Event Time']//1000))

        if metadata['P'] > np.abs(res['P']): response += '- price Chnaged by {}({}%)\n'.format(res['p'], res['P'])
        if metadata['Q'] > np.abs(res['Q']): response += '- Big Trade of {}\n'.format(res['Q'])
        if metadata['n'] > np.abs(res['n']): response += '- Total Trades in past 24hrs {}\n'.format(res['n'])
        response += '::Additional Info::\n'
        response += '\n\nAverage Price:{}\n First Trade Price:{}\n BaseVolume:{}'.format(metadata['w'], metadata['x'], metadata['v'])
        
        if notify: self.alerts.flock(self.bot['paisheeBot'], response)
        return response


    def Tickers(self, res):
        try:
            for scope, meta in self.Ticker.items(): #ticker in config
                if scope is 'default': map(lambda m: self.parseTicker(meta, m, True), filter(lambda s: s['s'].endswith('USDT'), res))
        except Exception as ex:
            print(ex)


    def mods(self, df) -> DataFrame:
        df['CandleColor'] = df.apply(lambda x: 'Red' if (x['open'] - x['close']) > 0 else 'Green', axis=1)
        df['Change'] = np.log(df['close'] / df['close'].shift(1)) * 100
        df['HL'] = df['high'] - df['low']        
        df['OC'] = np.abs(df['open'] - df['close'])
        df['Noise'] = df['HL'] - df['OC'].apply(np.abs)
        df['Noise%'] = ((df['HL'] - df['OC'])//df['HL']) * 100

        return df