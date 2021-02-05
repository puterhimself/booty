from datetime import date
from typing import Any
import pandas as pd


_B_cols_T  = ['DateTime', 'Open', 'High', 'Low', 'Close', 'Volume', 'Closetime', 'Quoteassetvolume', 'Trades', 'Basetbav', 'Quotetbav', 'Ignore']

_B_cols_L  = ['datetime', 'open', 'high', 'low', 'close', 'volume', 'closetime', 'quoteassetvolume', 'trades', 'basetbav', 'quotetbav', 'ignore']

_cols_L =  ['datetime', 'open', 'high', 'low', 'close', 'volume', 'quoteassetvolume', 'trades']

_cols_T =  ['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume', 'Quoteassetvolume', 'Trades']

_cols = _cols_L

_kline = ['datetime', 'closetime', 'symbol', 'interval', 'firstID', 'lastID', 'open', 'close', 'high', 'low', 'volume', 'trades', 'x', 'quoteassetvolume', 'basetbav', 'quotetbav', 'ignore']

_kline_T = ['Datetime', 'Closetime', 'Symbol', 'Interval', 'Firstid', 'Lastid', 'Open', 'Close', 'High', 'Low', 'Volume', 'Trades', 'X', 'Quoteassetvolume', 'Basetbav', 'Quotetbav', 'Ignore']

aggVars = aggVars_L = {
    'datetime': 'first',
    'open': 'first',
    'high': 'max',
    'low': 'min',
    'close': 'last',
    'volume': 'sum',
    'trades': 'sum',
    'closetime': 'last',
    'quoteassetvolume': 'sum',
    'trades': 'sum',
    'basetbav': 'sum',
    'quotetbav': 'sum',
    'ignore': 'sum',
}

_aggVars_L = {
    'open': 'first',
    'high': 'max',
    'low': 'min',
    'close': 'last',
    'volume': 'sum',
    'trades': 'sum',
}

aggVars_T = {
    'Datetime': 'first',
    'Open': 'first',
    'High': 'max',
    'Low': 'min',
    'Close': 'last',
    'Volume': 'sum',
    'Trades': 'sum',
    'Closetime': 'last',
    'Quoteassetvolume': 'sum',
    'Trades': 'sum',
    'Basetbav': 'sum',
    'Quotetbav': 'sum',
    'Ignore': 'sum',
}

_aggVars_T = {
    'Open': 'first',
    'High': 'max',
    'Low': 'min',
    'Close': 'last',
    'Volume': 'sum',
    'Trades': 'sum',
}
meta = {
            'case': True,
            'dti': True,
            'localize': True,
            'update': True,
            'resample': pd.Timedelta,
            'from': date,
            'tf': str,
            'src': str,
            'dt': str,

            'coin': str,
            'market': str,
            'scrip': str,
            'scrips': list,
            
            'channels': list,
            'stream_label': str,
            'stream_buffer_name': str,
            'output': str,
            
            'df': pd.DataFrame,
            'context': str,
            'mod': Any,
            'mods': list,

            'card': str,
            '_cols': list,
        }