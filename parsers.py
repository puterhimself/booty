from alert import Alerts
from conf import Configuration
from datahandler import dataHandler
from binance.websockets import BinanceSocketManager as Socks


class StrategyParse(Configuration):
    
    def __init__(self, Strategy, metadata):
        super().__init__()
        self.handle = dataHandler()
        self.alerts = Alerts()
        self.sock = Socks(self.SpotClient)
        self.Strategy = Strategy

        self.data = self.handle.prefetchForStrategies(metadata)
        self.ws = self.handle.WebSocketForStrategies(metadata, self.sock, self.callback)
        

    def callback(self, res):
        print(res)
        self.bot['paisheeBot'].send_message(chat_id=1443973207, text='I am IN')
        res = self.handle.processResponse(res, True, self.data)
        if res.Is in ['true', True, 'True']: 
            for k, df in self.data.items():
                self.data[k] = self.Strategy.populate_indicators(df)
                self.data[k] = self.Strategy.populate_buy_trend(df)
                self.data[k] = self.Strategy.populate_sell_trend(df)

                self.alerts.stratsAlerts(k, df, self.bot['paisheeBot'])

    def run(self): pass