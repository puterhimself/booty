from operator import mod
import sys
import pandas as pd
from loguru import logger
from typing import Any, Dict

import const as c
from dataclasses import dataclass, field
from data.datadispenser import datadispenser


@dataclass
class datacard:
    # __slots__ = ['scrip', 'df', 'tf', 'mod']
    df: pd.DataFrame 
    scrip: str = None
    meta: Dict = None
    mod: Any = None
    
    @property
    def desc(self):
        return field(default_factory=lambda: {
            'df': self.df,
            'scrip': self.scrip,
            'meta': self.meta,
            'mod': self.mod,
        })

    def __getattr__(self, name):
        try:
            if str(name) in self.df.columns:
                return self.df[name]
        except KeyError:
            msg = "'{0}' object has no attribute '{1}'"
            raise AttributeError(msg.format(type(self).__name__, name))




class blocks(datadispenser):

    def __init__(self, coin, context: Any='live', market='USDT') -> None:
        super().__init__()
        logger.info(f'-> Block {coin}', meta={'market': market})

        self.coin = coin
        self.market = market
        self.scrip: str = f'{coin}-{market}'
        self._scrip: str = f'{coin}{market}'
        
        self.cards = pd.Series()
        self.init(context)
    
    # @logger.catch
    def init(self, context):
        if context is 'analysis':
            self.dfmeta = {'dt': 'datetime', 'localize': True}
            meta = {'src': 'csv'}
        
        elif isinstance(context, dict):
            self.dfmeta = context
            meta = context

        else:
            self.dfmeta = {'dt': 'datetime', 'localize': True,}
            meta = {'src': 'e', }

        try:
            self.base: datacard = datacard(
                self.burst(self._scrip, meta, market=self.market), 
                mod='default',
                scrip=self.scrip,
                meta=self.dfmeta
            )
            logger.bind(meta=meta, surplus=self.dfmeta).info(f'-> {self.scrip} with followed context')

        except Exception as e:
            logger.exception(f'{e} occurred in {self.scrip}')
            raise


    def __getattr__(self, name):
        try:
            if name in c._B_cols_L:
                return self.base.df[name]
            else: 
                return self.cards.at[name].df

        except KeyError:
            msg = "'{0}' object has no attribute '{1}'"
            raise AttributeError(msg.format(type(self).__name__, name))
    

    def __getitem__(self, name):
        try:
            if name in c._B_cols_L:
                return self.base.df[name]
            else: 
                return self.cards.at[name].df
        except KeyError:
            msg = "'{0}' object has no attribute '{1}'"
            raise AttributeError(msg.format(type(self).__name__, name))


    @property
    def df(self):
        # return self._df(self.meta)
        return self._df(self.dfmeta)
    
    @df.setter
    def setdf(self, inp): 
        if isinstance(inp, pd.DataFrame):
            self.base.df = inp
    
    @property
    def desc(self):
        return {
            'coin': self.coin,
            'market': self.market,
            'scrip': self.scrip,
            '_scrip': self._scrip,
            'cards': self.cards,
            'df': self.base
        }


    def mod(self, name: str, df: pd.DataFrame, *args, **kwargs):
        
        if name in self.cards.keys():
            logger.bind(meta={'card': name, 'scrip': self.scrip}).info(f'--card exists del it!')
            del self.cards[name]

        card = pd.Series({
            name : datacard(df, *args, **kwargs),
            })
        self.cards = self.cards.append(card)
        logger.bind(meta={'card': name, 'scrip': self.scrip}).info(f'-- Appending Card')

    
    def squeeze(self):
        logger.bind(meta={'scrip': self.scrip}).info(f'--updating base scrip')
        self.base.df = super().squeeze(self._scrip, self.base.df)
        
                
    def applystrat(self, modclass, meta={}):
        logger.bind(meta=meta).info(f'-> Applying {modclass.name} on {self._scrip}')
        
        logger.bind(meta=meta).debug(f'--generalizing df')
        df = self._df(meta).iloc[-modclass.startup_candle_count:]
        
        df = modclass.populate_indicators(df, {})
        df = modclass.populate_buy_trend(df, {})
        df = modclass.populate_sell_trend(df, {})
        df.fillna(0, inplace=True)
        logger.bind(meta=meta).debug(f'-- mods applied to from {modclass.name}')

        self.mod(modclass.name, df[meta['_cols']], scrip=self.scrip, mod=modclass, meta=meta)


    def _df(self, meta={}):

        """
        meta:
            'case': bool
            'dt': col name
            'dti': bool
            'localize': bool
            'fmt': str
            ver: str
        """
        logger.bind(meta=meta).debug(f'modifying {self.scrip} with followed meta')
            

        if 'card' in meta:
        
            if '-' in meta['card']: 
                vers = meta['card'].split('-')[-1]
                card = self.cards.at[vers]
                if 'resample' in card.meta:
                    meta['resample'] = card.meta['resample']

                df: pd.DataFrame = self.base.df.copy()
                df = self.garnish(df, meta)

                logger.bind(meta=meta).debug(f'-> fullsize df')
                df = pd.concat([df, card.df], axis=1, join='inner', copy=False)

                return df

            else:
                df = self.cards.at[meta['card']].df
                return df
        else:
            df: pd.DataFrame = self.base.df.copy()
            df = self.garnish(df, meta)
            return df
        
if __name__ == "__main__":
    btc = blocks('BTC')
    print(btc.df.tail())