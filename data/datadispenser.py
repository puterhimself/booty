import os

from loguru import logger
import const as c
import pandas as pd
from typing import Any, Dict
from conf import Configuration


class datadispenser(Configuration):
    
    # _cached = {}

    def __init__(self) -> None:
        super().__init__()
        logger.info('-> DataDispenser™')
        # self.stock = self.stash()


    def stash(self) -> dict:
        stock = {}
        localcsv = os.listdir(self._datadir)
        localcsv = [csv.split('.')[0] for csv in localcsv]
        logger.debug(f'-- local Files {localcsv}')
        
        # dbCollections = self._db.list_collection_names(filter = {"name": {"$regex": r"^(?!system\.)"}})
        # logger.debug(f'--cloud {dbCollections}')
        # stock['db'] = dbCollections
        # stock['mongo'] = dbCollections
        
        cexlist = self.exchange.get_exchange_info()['symbols']
        stock['csv'] = localcsv
        stock['local'] = localcsv
        stock['e'] = [sym['symbol'] for sym in cexlist]
        stock['binance'] = [sym['symbol'] for sym in cexlist]
        return stock


    @logger.catch
    def burst(self, scrip=None, meta: Dict=dict(), coin=None, market: Any='USDT')-> pd.DataFrame: 
        """
        metadata:   
            src: CSV, DB, Excahnge
            case : case lower or Title
            dt: column name
            localize: bool
            dti : bool
            'update': True
            resampl: timedelta
            frpm: date
        """
        df = pd.DataFrame()
        scrip = f'{coin}{market}' if scrip is None else scrip

        print(' o==[]::::::::::::::::> sup Boi!')
        logger.bind(meta=meta).debug(f'bustin\' {scrip} in here man~')
        if 'src' in meta and meta['src'] in ['local', 'csv', '', 'CSV']:

            # if scrip in self.stock['csv']:
                meta['file'] = os.path.join(self._datadir, f'{scrip}.csv')
                df = pd.read_csv(meta['file'], header=None)
                logger.bind(meta=meta).debug(F"Loading {scrip} from csv")
        

        if 'src' in meta and meta['src'] in ['DB', 'db', 'cloud', 'mongo']:
            
            # if scrip in self.stock['db']:
                df = list(self._db[scrip].find({}))
                df = pd.DataFrame(df)
                logger.bind(meta=meta).debug(F"{scrip} reading from cloud")

        
        if 'update' in meta and meta['update']: 
            datadispenser.squeeze(scrip, df, meta)
        
        if df.empty:
            df = self.refill(scrip, meta)
        
        df = self.garnish(df, meta)

        return df.dropna(how='any')


    def refill(self, scrip, meta: Dict={}) -> pd.DataFrame: 
        """
        meta:
            scrip
            tf
            from:

        """
        tf = '1m' if 'tf' not in meta else meta['tf']
        kabse = '1 day ago UTC' if 'from' not in meta else meta['from']

        df = self.exchange.get_historical_klines(scrip, tf, kabse)
        df = pd.DataFrame.from_records(df).astype(float)
        return df

    @logger.catch
    def squeeze(self, scrip, df: pd.DataFrame, meta: Dict={}):
        """
        meta:
            src: db, csv, both, return
            from
            update
            same meta used for input df
            any other df meta used
        """
        meta['from'] = int(df.iloc[-1, 0])
        meta['update'] = False
        meta['src'] = 'e'

        if not df.empty: 
            pull = self.burst(scrip=scrip, meta=meta)
            df = pd.concat([df, pull], ignore_index=True)
            _dtcol = df.columns[0]
            df.drop_duplicates(_dtcol, keep='last', inplace=True, ignore_index=True)

            if 'save' in meta and meta['save']:
                if meta['src'] in ['local', 'csv', '', 'CSV']:
                    df.to_csv(meta['file'], index=False, header=False)
        
        return df


    @logger.catch
    def garnish(self, df: pd.DataFrame, meta: Dict={}): 

        """
        meta:
            dti: bool
            datetimecolumn: to implement if need be
            case: L,t,T, title....
            fmt: binance, core, custom
            localize: Asia/Kolkata
            mod: func which takes df as input and returns df
            resample: False or pd.Timeframe
        """
        # if 'case' in meta and meta['case']: df.columns = c._B_cols_T
            # df.columns = [str(colz).capitalize() for colz in df.columns]

            # if 'fmt' in meta:
            #     if meta['fmt'] in ['c', 'C', 'core', 'def', None]: df.columns = c._cols_T
            #     if meta['fmt'] in ['b', 'binance', 'e', 'E', 'cex']: df.columns = c._B_cols_T
        # else:   df.columns = c._B_cols_L
            # df.columns = [str(colz).lower() for colz in df.columns]
            # if 'fmt' in meta:

            #     if meta['fmt'] in ['c', 'C', 'core']: 
            #         df.columns = c._cols_L
                    
            #     if meta['fmt'] in ['b', 'binance', 'e', 'E', 'cex']: 
            #         df.columns = c._B_cols_L

        if 'case' in meta and meta['case']: df.columns = c._B_cols_T
        else:   df.columns = c._B_cols_L

        if 'dt' in meta:
            _dt = df.columns[0]
            _dtcol = _dt if meta['dt'] in [True, _dt] else meta['dt']
            df[_dtcol] = pd.to_datetime(df[_dt], utc=True, unit='ms')

            if 'resample' in meta and meta['resample']:
                if 'dti' in meta and meta['dti']:
                    df = df.resample(meta['resample'], on=_dtcol).apply(c.aggVars).reset_index(drop=False)
                else: df = df.resample(meta['resample'], on=_dtcol).apply(c.aggVars).reset_index(drop=True)
            
            if 'localize' in meta and meta['localize']: 
                df[_dtcol] = df[_dt].dt.tz_convert('Asia/Kolkata')

            try:
                if 'dti' in meta and meta['dti']:
                    df.set_index(_dtcol, inplace=True, drop=True)
            except KeyError:
                print('dti set by resampling')
        
        if 'dropna' in meta and meta['dropna']:
            df.dropna(how='any', inplace=True, )
        
        if 'fillna' in meta and meta['fillna']:
            df.fillna(0, inplace=True)
        
        return df


    def sleeve(self, scrips, meta={}):
        streamID = self.ws.create_stream(markets=list(scrips), **meta)
        return streamID