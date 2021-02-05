import schedule
import pandas as pd
from data.databox import databox



class processor():

    def logicalize(self, box: databox):
        meta = {}
        box.squeeze()
        meta['update'] = 'done Updating'
        meta['mods'] = str(box.strategiesList)
        meta['scrips'] = str(box._scrips)

        for name, st in box.Strats.items(): 
            box.applystrat(st, {})
            meta[name] = self.getMeta(st)

        return meta


    def understand(self, box: databox) -> dict:
        meta = {}

        for strat in box.Strats.values():
            meta['strategy'] = strat.name
            meta['tf'] = strat.timeframe
            meta['sl'] = strat.stoploss

            for scrip, block in box.scrips.items():

                meta['scrip'] = scrip
                signal = block._df(meta={'card': strat.name})

                if 1 in signal.buy.values[-3:]:  
                    meta['side'] = 'buy'
                    yield meta

                elif 1 in signal.sell.values[-3:]:
                    meta['side'] = 'sell'
                    yield meta
        
                

    def run(self,):
        # dataloop = Thread(target=self.df.live)
        schedule.every(62).seconds.do(self.logicalize)
        schedule.every(62).seconds.do(self.understand)

        while True:
            schedule.run_pending()

    # def getcalc
    # CONFIG WISE CALC OVER DATABLOCK
    # get LERTS check conditions
    
    # DEF SEND ALERTS