import sys
import const as c
import pandas as pd
from loguru import logger
from data.blocks import blocks
from data.datadispenser import datadispenser
import data.datahelper as dh


class databox(datadispenser):

    def __init__(self, coins: list = None, context='live',  markets: list= ['USDT'], name='theBox™') -> None:
        super().__init__()
        logger.info('-> DataBox')
        self.mods = []


        self._coins = self.pairs if coins is None else coins
        logger.debug(f'-- Coins: {self._coins}')
        self._markets = markets
        logger.debug(f'-- markets: {self._markets}')
        self._scrips = [f'{_c}{_m}' for _c in self._coins for _m in self._markets]
        logger.debug(f'-- scrips: {self._scrips}')
        self._stock = self.stash()
        self.scrips = pd.Series({coin: blocks(coin, context) for coin in self._coins}, name=name)
        logger.info(f'-- with context {context}, {self._scrips} init')



    def __getattr__(self, name):
        try:
            if name is not 'scrips' and name in self.scrips.keys():
                return self.scrips.at[name].df

        except KeyError:
            msg = "'{0}' object has no attribute '{1}'"
            raise AttributeError(msg.format(type(self).__name__, name))
    
    
    def __getitem__(self, name):
        try:
            if name in self.scrips.keys():
                return self.scrips.at[name].df

        except KeyError:
            msg = "'{0}' object has no attribute '{1}'"
            raise AttributeError(msg.format(type(self).__name__, name))    

    @property
    def desc(self):
        meta = {
            # 'coin': ' | '.join(self._coins),
            # 'market': ' | '.join(self._markets),
            'scrips': ' | '.join(self._scrips),
            '_scrips': self._scrips,
            'mods': ' | '.join(self.mods),
            '_mods': self.mods,
            'strats': '|'.join(self.strategiesList),
            '_strats': self.strategiesList,
            'btconf': '|'.join(dh.backtestinit),
        }
        return meta
    

    def loads(self, coin=None, market='USDT', context='live', name='theBox™'):
        scrip = f'{coin}{market}'

        if coin in self._stock['e']:
            scrip = pd.Series({coin: blocks(coin, context, market)})
            self.scrips.append(scrip)
            logger.info(f'-- appending {coin} to theBox™ with context {context}')
        else:
            logger.bind(meta={'scrip': scrip}).warning('Invalid scrip')

    

    def mapply(self, attr, *args, **kwargs):
        self.scrips.apply(lambda scrip: getattr(scrip, attr)(*args, **kwargs))
        

    def squeeze(self):
        self.scrips.apply(lambda scrip: scrip.squeeze())


    def mod(self, name, func, *args, **kwargs):
        self.scrips.apply(
            lambda scrip: scrip.mod(name, func(scrip, *args, **kwargs), )
        )
        self.mods.append(name)

    def applystrat(self, modclass, meta={}, *args, **kwargs):
        self.scrips.apply(
            lambda scrip: scrip.applystrat(modclass, meta, *args, **kwargs)
        )
        self.mods.append(f'~{modclass.name}')
    

    def applyBacktest(self, modclass, meta={}, *args, **kwargs):
         meta = {
            'case': True,
            'dt': True,
            'localize': True,
            'card': f'-{modclass.name}',
            }
    

    def klinestream(self):
        meta = {
            'channels': ['kline_1m'],
            'stream_label': self.name,
            'stream_buffer_name': self.name,
            'output': 'dict'
        }
        streamID = self.sleeve(self.scrips.keys(), meta)
        
        while True:
            if self.ws.is_manager_stopping(): sys.exit(0) 
        
            res = self.ws.pop_stream_data_from_stream_buffer(self.name)
            if 'data' in res:
                if res['data']['x']:
                    res = res['data']['k'].values()
                    res: pd.DataFrame = pd.DataFrame.from_dict(
                        {idx: val for idx, val in zip(c._kline, res) }
                    )
                    self.scrips[res.symbol].df = res[c._B_cols_L]    