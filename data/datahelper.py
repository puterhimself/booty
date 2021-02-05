from data.blocks import blocks
from dataclasses import dataclass, field
from typing import Any, Callable, Dict
import pandas as pd



backtestinit = {
            'cash': 'cash is the initial cash to start with.',
            'commission': 'commis is the commission ratio. E.g. if your brokers commission is 1% of trade value, set commission to `0.01`. Note, if you wish to account for bid-ask spread, you can approximate doing so by increasing the commission, e.g. set it to `0.0002` for commission-less forex trading where the average spread is roughly 0.2‰ of asking price.',
            'margin': 'margin is the required margin (ratio) of a leveraged account. No difference is made between initial and maintenance margins. To run the backtest using e.g. 50:1 leverge that your broker allows, set margin to `0.02` (1 / leverage).',
            'trade_on_close': 'IF its `True`, market orders will be filled with respect to the current bars closing price instead of the next bars open.',
            'hedging': ' is `True`, allow trades in both directions simultaneously. If `False`, the opposite-facing orders first close existing trades in a [FIFO] manner.',
            'exclusive_orders': ' is `True`, each new order auto-closes the previous trade/position, making at most a single trade (long or short) in effect at each time.'
            }

def stratmeta(modclass) -> dict:
        return {
            keez: getattr(modclass, keez) for keez in 
            [attr for attr in dir(modclass) 
            if not callable(getattr(modclass, attr)) and not attr.startswith("__")]}


@dataclass
class datacard:
    # __slots__ = ['scrip', 'df', 'tf', 'mod']
    df: pd.DataFrame = None
    meta: Dict = None
    mod: Any = None
    scrip: str = None
    coin: str = None
    market: str = None
    apply: Callable = None
    block: blocks = None


    @property
    def df(self):
        # df = self.block._df(self.meta)
        return self.apply(meta=self.meta, mod=self.mod)
    
    @property
    def desc(self):
        return field(default_factory=lambda: {
            'df': self.df,
            'scrip': self.scrip,
            'meta': self.meta,
            'mod': self.mod,
        })