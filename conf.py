import os
import telegram
import yaml
from telegram.ext import Updater 
from binance.client import Client
from binance_f import RequestClient as Fut
from binance_f.base.printobject import *


class Configuration():

    def __init__(self):

        with open('userData/config/config.yml', 'r') as config_file:
            default_config = yaml.load(config_file)

        if os.path.isfile('defaults.yml'):
            with open('config.yml', 'r') as config_file:
                user_config = yaml.load(config_file)
        else:
            user_config = dict()

        self.settings = default_config['Settings']
        self.Telegram = default_config['Telegram']
        self.bot = {k: telegram.Bot(token=v) for k, v in self.Telegram['bots'].items()}

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



if __name__ == "__main__":
    c = Configuration()
    obj = c.Strats['MA']
    print(obj.stoploss)
