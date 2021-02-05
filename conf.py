import os
import sys
import yaml
import _log
from loguru import logger

# import pymongo
# from pymongo.database import Database
import telegram
from telegram.ext import Updater
from binance.client import Client
from unicorn_binance_websocket_api.unicorn_binance_websocket_api_manager import BinanceWebSocketApiManager as wsapi

class Configuration():

    def __init__(self) -> None:
        cFile = os.path.join('userdata', 'config', 'config.yml')
        self.config = self.conf(cFile)


    @logger.catch
    def conf(self, cFile=None) -> None:

        with open(cFile, 'r') as config_file:
            default_config = yaml.load(config_file, Loader=yaml.FullLoader)

        log = default_config['log']
        self._log = _log.setup_logging(log)
        # self._dburl = default_config['data']['_dburl']
        # self.mongoSync = pymongo.MongoClient(self._dburl)
        # self._db: Database = self.mongoSync.scrip

        logger.configure(**self._log)
        logger.info('👋≧◉ᴥ◉≦ Greetings maSter')
        logger.info('init vars')
        self._datadir = default_config['data']['_datadir']
        self._stratdir = default_config['data']['_stratdir']
        self.creds: list = [default_config['exchange']['binance']['api'], default_config['exchange']['binance']['secret']]

        self.exchange: Client = Client(*self.creds)
        self.ws = wsapi(exchange=default_config['exchange']['ws'], output_default='dict')
        self._cex = self.exchange
        logger.debug(f'-- BinanceExchange {self._cex}')

        
        
        self.updater: Updater = Updater(token=default_config['Telegram']['bot']['p'], use_context=True)
        self.updater_: Updater = Updater(token=default_config['Telegram']['bot']['k'], use_context=True)
        self.bot: telegram.bot = self.updater.bot
        self._Tusers: dict = default_config['Telegram']['users']
        logger.debug(f'-- Telegram, ')

        self.pairs:list = default_config['alerts']['pairs']
        if self.pairs is 'local':
            self.pairs = [mc.split('USDT')[0] for mc in os.listdir(self._datadir)]
            #!regex split
        logger.debug(f'-- pairs: {self.pairs}')

        
        self.prizes: dict = default_config['alerts']['price']
        logger.debug(f'-- Prize alerts: {self.prizes}')

        
        self.strategiesList: list = default_config['alerts']['strategies']
        if self.strategiesList is 'all':
            self.strategiesList = [mc.split('.')[0] for mc in os.listdir(self._stratdir) if not mc.startswith('__')]
        logger.debug(f'-- strats: {self.strategiesList}')
        
        mod = __import__(self._stratdir.replace('/', '.'), fromlist=self.strategiesList)
        self.Strats = {strat : getattr(getattr(mod, strat), strat)() for strat in self.strategiesList}
        logger.info('Done loading vars!')

        return default_config
