import os
import const as c
import pandas as pd
from os.path import join
from typing import Any, Callable, Dict
from data.datadispenser import datadispenser
from dataclasses import dataclass

@dataclass
class datacard:
    # __slots__ = ['scrip', 'df', 'tf', 'mod']
    df: pd.DataFrame 
    scrip: str = None
    meta: Dict = None
    mod: Any = None
    TF: str = '1m'
    tf: str = '1min'

    @property
    def base(self):
        if self.scrip[-4:] is 'USDT':   return self.scrip[:-4]
        else: return self.scrip
    
    @property
    def quote(self):
        if self.scrip[-4:] is 'USDT':   return 'USDT'
        else: return self.scrip

    @property
    def context(self):
        return 'live' if self.df.shape[0] > 1000 else 'analysis'
    

    def apply(self, *args, **kwargs):
        # if isinstance(self.mod, callable):pass
        self.df = self.mod(*args, **kwargs)
    

    def __getattr__(self, name):
        try:
            if str(name) in self.df.columns:
                return self.df[name]
        except KeyError:
            msg = "'{0}' object has no attribute '{1}'"
            raise AttributeError(msg.format(type(self).__name__, name))




class blocks(datadispenser):

    def __init__(self, scrip, context: Any='live') -> None:
        super().__init__()
        self.cards = pd.Series()
        self.coin = 'single coins for future'
        self.scrip: str = scrip
        # self.store: Dict[str, datacard] = {}

        self.init(context)
    

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

        # self.store['default'] = datacard(self.scrip, self.burst(self.scrip, meta), mod='default')
        # self.base: datacard = self.mod()
        self.base: datacard = datacard(self.burst(self.scrip, meta), mod='default')


    def __getattr__(self, name):
        try:
            if name in c._B_cols_L:
                return self.base.df[name]

            elif name in self.cards.keys():
                return self.cards.at[name].df
                
            else:
                raise AttributeError(f'{name} Not Found:')

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
            if inp.shape[0] is 1:
                self.base = pd.concat([self.base, inp])


    def mod(self, name: str, df: pd.DataFrame, *args, **kwargs):
        card = pd.Series({
            name : datacard(df, *args, **kwargs),
            })
        self.cards = self.cards.append(card)

    
    def squeeze(self):
        self.base.df =  super().squeeze(self.scrip, self.base.df)
        
                
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
            
        df: pd.DataFrame = self.base.df.copy()
        df = self.garnish(df, meta)

        if 'card' in meta:
            if '-' in meta['card']: 
                vers = meta['card'].split('-')[-1]
                df = pd.concat([df, self.cards.at[vers]], axis=1, join='inner', copy=False)

            if meta['card'] in self.cards:             
                df = self.cards.at[meta['card']].df
        
        return df