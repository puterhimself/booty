import os
from binance.websockets import BinanceSocketManager
import pandas as pd
from datetime import date
from binance.enums import *
from conf import Configuration


class dataHandler(Configuration):
    def __init__(self) -> None:
        super().__init__()
        self.Name = ['openTime', 'open', 'high', 'low', 'close', 'volume', 'CloseTime', 'QuoteAssetVolume', 'NumberOfTrades', 'BaseTBAV', 'QuoteTBAV', 'Ignore']
        # self.spotSock = Socks(self.SpotClient)
        # self.futSock = Socks(self.FutClient)
        # self.connKeys = {}
        # self.df = {}


    def Scrip(self, scrip, interval='1m', From='1 Aug, 2017', Till=None, save=False, update=False, file=None):
        file = 'userData/data/{}-{}.csv'.format(scrip, interval) if file is None else file
        Till = date.today().strftime('%d %b, %Y') if Till is None else Till
        temp = pd.DataFrame()
        try:
            if update: 
                temp = pd.read_csv(file)
                temp['dt'] = pd.to_datetime(temp['OpenTime'], unit='ms')
                From = temp['dt'].iloc[-1]
                
                temp = temp.drop(index=temp.loc[temp['dt'].dt.date == From].index)
                temp = temp.drop(columns='dt')
                temp = temp.append(self.Scrip(scrip, From=From.strftime('%d %b, %Y'), interval=interval))
            else:
                temp = self.SpotClient.get_historical_klines(scrip, interval, From)
                temp = pd.DataFrame.from_records(temp, columns=self.Name)
        except Exception as ex:
            print(ex)
        
        if save: temp.to_csv(file, index=False); return
            
        return temp
        

    def WebSocketForStrategies(self, metadata, sock, callback):
        streams = []; interval = metadata['interval']

        if metadata['scope'] == 'all': streams = ['{}@kline_{}'.format(scrip, interval) for scrip in self.FutSymbols]
        elif metadata['scope'] == 'custom': streams = ['{}@kline_{}'.format(scrip, interval) for scrip in metadata['scrips']]
        else: streams = [str('{}@kline_{}'.format(scrip, interval)).lower() for scrip in self.scrips]

        streams = set(streams)
        cKey = sock.start_multiplex_socket(streams=streams, callback=callback)
        print('spotsocket updated for streams:{}'.format(streams))
        return cKey

    
    def getScrip(self, scrip=None, interval='15m', From='2 days ago UTC', update=False, ws=False, save=False): 
        file = 'userData/data/{}-{}.csv'.format(scrip, interval); df = pd.DataFrame()
        if os.path.isfile(file):
            if update: df = self.Scrip(scrip, interval, update=True)
            else: df = pd.read_csv(file, names=self.Name)
        
        else: 
            df = self.Scrip(scrip, interval, From)
        
        if save: df.to_csv(file, index=False)

        return df


    def prefetchForStrategies(self, metadata):
        print('Fetching Data------')
        interval = metadata['interval']
        days = '{} days ago UTC'.format(metadata['lookbackDays'])
        
        if metadata['scope'] == 'all': 
            print('interval = {}, lookback = {} , scrips = {}'.format(interval, days, 'All'))
            df = {scrip: self.getScrip(scrip, interval, days, update=True)  for scrip in self.FutSymbols}
        
        elif metadata['scope'] == 'custom': 
            print('interval = {}, lookback = {} , scrips = {}'.format(interval, days, 'custom'))
            df = {scrip: self.getScrip(scrip, interval, days, update=True)
                for scrip in metadata['scrips']}

        else: 
            print('interval = {}, lookback = {} , scrips = {}'.format(interval, days, 'default'))
            df = {scrip: self.getScrip(scrip, interval, days, update=True)  for scrip in self.scrips}
        
        return df


    def processResponse(self, res, dataAppend=False, df=None):
        if res['e'] == 'kline':
            name = "opentime, closetime, Symbol, Interval, First trade ID, Last trade ID, open, close, high, low, volume, NumberOfTrades, Is, QuoteAssetVolume, BaseTBAV, QuoteTBAV, Ignore"; name = name.split(',')
            
            res = pd.DataFrame.from_dict({k : [v] for k,v in zip(name, res['k'])})
            
            if res.Is in ['true', True, 'True'] and dataAppend and df is not None:
                df[res.Symbol] = df[res.Symbol].append(res[self.Name], ignore_index=True)
            
        return res


if __name__ == "__main__":  
    pass
        