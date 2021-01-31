import os
import sys
import yaml
import pymongo
import telegram
from pymongo.database import Database
from telegram.ext import Updater
from binance.client import Client
from unicorn_binance_websocket_api.unicorn_binance_websocket_api_manager import BinanceWebSocketApiManager as wsapi

class Configuration():

    def __init__(self) -> None:
        cFile = os.path.join('userdata', 'config', 'config.yml')
        self.conf(cFile)

    def conf(self, cFile=None) -> None:

        with open(cFile, 'r') as config_file:
            default_config = yaml.load(config_file, Loader=yaml.FullLoader)
        

        self._dburl = default_config['data']['_dburl']
        self.mongoSync = pymongo.MongoClient(self._dburl)
        self._db: Database = self.mongoSync.scrip

        self._datadir = default_config['data']['_datadir']
        self._stratdir = default_config['data']['_stratdir']
        self.creds: list = [default_config['exchange']['binance']['api'], default_config['exchange']['binance']['secret']]

        self.exchange: Client = Client(*self.creds)
        self._cex = self.exchange
        self.ws = wsapi(exchange=default_config['exchange']['ws'], output_default='dict')
        
        self.bot: telegram.Bot = telegram.Bot(token=default_config['Telegram']['bot'])
        self._Tusers: dict = default_config['Telegram']['users']

        self.pairs:list = default_config['alerts']['pairs']
        self.strategiesList: list = default_config['alerts']['strategies']
        self.prizes: dict = default_config['alerts']['price']
        
        mod = __import__(self._stratdir.replace('/', '.'), fromlist=self.strategiesList)
        self.Strats = {strat : getattr(getattr(mod, strat), strat) for strat in self.strategiesList}



        # --------------------------------------------------------------------

        # self.settings = default_config['Settings']
        # self.bot = {k: telegram.Bot(token=v) for k, v in self.Telegram['bots'].items()}
        # self.commander = {k: Updater(token=v, use_context=True) for k, v in self.Telegram['bots'].items()}

        
        # if 'stratsFolder' in self.settings: 
        #     self.stratFolder = self.settings['stratsFolder']
        #     self.stratFolder = self.stratFolder.replace('/', '.')

        # if 'Strats' in default_config:
        #     self.modclass = {k: v for k,v in default_config['Strats'].items()}

        # if 'PriceAlerts' in default_config:
        #     self.Ticker = default_config['PriceAlerts']['dayTicker']
        #     self.Trade = default_config['PriceAlerts']['Depth']
        #     self.Depth = default_config['PriceAlerts']['Trade']

        # self.sock = Socks(self.SpotClient)
        # self.conns = {}


if __name__ == "__main__":
    print(sys.path)
