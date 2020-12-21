import os
import sys
import pandas as pd
from numpy import dtype
from binance.enums import *
from conf import Configuration
from datetime import date, datetime


class dataHandler(Configuration):
    def __init__(self) -> None:
        super().__init__()
        self.Name = ['openTime', 'open', 'high', 'low', 'close', 'volume', 'closeTime', 'QuoteAssetVolume', 'NumberOfTrades', 'BaseTBAV', 'QuoteTBAV', 'Ignore']
        self.NameDtypes = [dtype('int64'), dtype('float64'), dtype('float64'), dtype('float64'), dtype('float64'), dtype('float64'), dtype('int64'), dtype('float64'), dtype('int64'), dtype('float64'), dtype('float64'), dtype('float64')]
        self.NameDtypes = {k: v for k,v in zip(self.Name, self.NameDtypes)}

        self.metadata = {'interval': '1m', 'save': True, 'From': 2, 'scope': 'def'}
        self.data = self.prefetchData(self.metadata)
        self.klineres = {}
        self.stratdf = {}
        # self.marketStream = self.ws(self.sock, ['!ticker@arr'], self.callback)


    def Scrip(self, scrip, interval='1m', From='1 Aug, 2017', Till=None, save=False, update=False, file=None):
        file = os.path.join(sys.path[0], 'userData','data/{}-{}.csv'.format(scrip, interval)) if file is None else file
        Till = date.today().strftime('%d %b, %Y') if Till is None else Till
        if update:
            temp = pd.read_csv(file)
            temp = temp.dropna()
            temp['dt'] = pd.to_datetime(temp['openTime'], unit='ms')
            From = temp['dt'].iloc[-1].date()
            
            temp = temp.drop(index=temp.loc[temp['dt'].dt.date == From].index, columns='dt')
            fetched = self.Scrip(scrip, From=From.strftime('%d %b, %Y'), interval=interval)
            temp = pd.concat([temp, fetched])
        else:
            temp = self.SpotClient.get_historical_klines(scrip, interval, From)
            temp = pd.DataFrame.from_records(temp, columns=self.Name)
        
        if save: temp.to_csv(file, index=False); print('saving Df'); return
        return temp
        

    def klineStream(self, metadata, sock, callback):
        streams = []; interval = metadata['interval']

        if metadata['scope'] == 'all': streams = ['{}@kline_{}'.format(scrip, interval) for scrip in self.FutSymbols]
        elif metadata['scope'] == 'custom': streams = ['{}@kline_{}'.format(scrip, interval) for scrip in metadata['scrips']]
        else: streams = [str('{}@kline_{}'.format(scrip, interval)).lower() for scrip in self.scrips]

        streams = set(streams)
        cKey = sock.start_multiplex_socket(streams=streams, callback=callback)
        print('spotsocket updated for streams:{}'.format(streams))
        return cKey

    
    def getScrip(self, scrip=None, interval='1m', From='2 days ago UTC', update=False, save=False): 
        # file = 'userData/data/{}-{}.csv'.format(scrip, interval)
        file = os.path.join(sys.path[0], 'userData','data/{}-{}.csv'.format(scrip, interval))

        if os.path.isfile(file):
            print('{} found locally, now reading....'.format(scrip))
            df = pd.read_csv(file)
            if update: df = self.Scrip(scrip, interval, update=True); print('updating File')
        
        else: 
            print('{} not found, fetching from Exchange'.format(scrip)); 
            df = self.Scrip(scrip, interval, From)
        
        if save: df.to_csv(file, index=False)
        return df.astype(self.NameDtypes)


    def prefetchData(self, metadata):
        print('Fetching Data------')
        interval = metadata['interval']
        days = '{} days ago UTC'.format(metadata['From']) if type(metadata['From']) is int else metadata['From']
        save = metadata['save'] or False

        if metadata['scope'] == 'all': print('interval = {}, lookback = {} , scrips = {}'.format(interval, days, 'All')); df = {scrip: self.getScrip(scrip, interval, days, update=True, save=save)  for scrip in self.FutSymbols}
        elif metadata['scope'] == 'custom': print('interval = {}, lookback = {} , scrips = {}'.format(interval, days, 'custom')); df = {scrip: self.getScrip(scrip, interval, days, update=True, save=save) for scrip in metadata['scrips']}
        else: 
            print('interval = {}, lookback = {} , scrips = {}'.format(interval, days, 'default'))
            df = {scrip: self.getScrip(scrip, interval, days, update=True, save=save)  for scrip in self.scrips}
        return df


    def processResponse(self, res):
        name = "openTime,closeTime,Symbol,Interval,First trade ID,Last trade ID,open,close,high,low,volume,NumberOfTrades,x,QuoteAssetVolume,BaseTBAV,QuoteTBAV,Ignore"; name = name.split(',')
        res = pd.DataFrame.from_dict({k : [v] for k,v in zip(name, res['k'].values())})
        
        # if res['e'] == '24hrTicker':
        #     name = ['Event Type', 'Event time',  'Symbol',  'Price change',  'Price change percent',  'Weighted average price',  'First trade',  'Last price',  'Last quantity',  'Best bid price',  'Best bid quantity',  'Best ask price',  'Best ask quantity',  'Open price',  'High price',  'Low price',  'Total traded base asset volume',  'Total traded quote asset volume',  'Statistics open time',  'Statistics close time',  'First trade ID',  'Last trade Id',  'Total number of trades']
        #     res = pd.DataFrame.from_dict({k : [v] for k,v in zip(name, res.values())})
            
        return res


    def ws(self, sock, streams, callback, start=False, run=False):
        # streams = [str('{}@kline_1m'.format(scrip)).lower() for scrip in self.scrips]
        cKey = sock.start_multiplex_socket(streams=streams, callback=callback)
        if start: sock.start()
        if run: sock.run()
        return cKey


    def updateDF(self, data, resdf):
        scrip = resdf['Symbol'].iloc[-1]
        resdf = resdf[self.Name].astype(self.NameDtypes)
        # data[scrip] = data[scrip].append(resdf, ignore_index=True).reset_index(drop=True)
        data[scrip] = pd.concat([data[scrip], resdf], ignore_index=True)
        print('{} updated'.format(scrip))
        
        return data
    

    def Grouper(self, df, freq, aggVars=None, key='openTime'):
        aggVars = {
        'openTime': 'first',
        'open': 'first',
        'close': 'last',
        'high': 'max',
        'low': 'min',
        'closeTime': 'last',
        'volume': 'sum',
        'QuoteAssetVolume': 'sum',
        'NumberOfTrades': 'sum',
        'BaseTBAV': 'sum',
        'QuoteTBAV': 'sum',
        } if aggVars is None else aggVars
        df[key] = pd.to_datetime(df[key], unit='ms')
        df = df.groupby(pd.Grouper(key=key, freq=freq)).agg(aggVars).reset_index(drop=True)
        
        return df
