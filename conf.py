import os
import sys
import yaml
import telegram
from telegram.ext import Updater
from binance.client import Client
from binance_f.base.printobject import *
from binance_f import RequestClient as Fut
from binance.websockets import BinanceSocketManager as Socks


class Configuration():

    def __init__(self):
        cFile = os.path.join(sys.path[0], 'userData', 'config/config.yml')
        with open(cFile, 'r') as config_file:
            default_config = yaml.load(config_file)

        self.settings = default_config['Settings']
        self.Telegram = default_config['Telegram']
        self.bot = {k: telegram.Bot(token=v) for k, v in self.Telegram['bots'].items()}
        self.commander = {k: Updater(token=v, use_context=True) for k, v in self.Telegram['bots'].items()}

        if 'scrips' in self.settings:
            self.scrips = self.settings['scrips']
        
        if 'stratsFolder' in self.settings: 
            self.stratFolder = self.settings['stratsFolder']
            self.stratFolder = self.stratFolder.replace('/', '.')

        if 'Exchange' in default_config:
            self.Exchange = default_config['Exchange']['binance']
            
            if 'api' and 'secret' in self.Exchange:
                self.FutClient = Fut(api_key=self.Exchange['api'], secret_key=self.Exchange['secret'])
                self.SpotClient = Client(self.Exchange['api'], self.Exchange['secret'])
            
            if self.FutClient:
                # self.FutSymbols = self.FutClient.get_exchange_information()
                # self.FutSymbols = self.FutSymbols.symbols
                # self.FutSymbols = set([sym.symbol for sym in self.FutSymbols])
                self.FutSymbols = {}

        if 'Strats' in default_config:
            self.modclass = {k: v for k,v in default_config['Strats'].items()}
            mod = __import__(self.stratFolder, fromlist=self.modclass.keys())
            self.Strats = {strat : getattr(getattr(mod, strat), strat) for strat in self.modclass.keys()}

        if 'PriceAlerts' in default_config:
            self.Ticker = default_config['PriceAlerts']['dayTicker']
            self.Trade = default_config['PriceAlerts']['Depth']
            self.Depth = default_config['PriceAlerts']['Trade']

        self.sock = Socks(self.SpotClient)
        self.conns = {}


if __name__ == "__main__":
    print(sys.path)
