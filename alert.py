import time
import numpy as np
from conf import Configuration


class Alerts(Configuration):

    def __init__(self):
        super().__init__()

    def priceAlerts(self, scrip, zones, template=None):pass
    def volAlerts(self, scrip, range, timeframe):pass    
    
    def flock(self, bot, txt):
        for _, id in self.Telegram['users'].items():
            bot.send_message(chat_id=id, text=txt)
            time.sleep(0.05)
            

    def stratsAlerts(self, data, meta):
        bot = self.bot[meta['bot']]
        for scrip, df in data.items():

            if 1 in df['buy'].iloc[-3:]:
                text = 'buy triggered for {}'.format(scrip)
                self.flock(bot, text)
            
            if 1 in df['sell'].iloc[-3:]:
                text = 'sell triggered for {}'.format(scrip)
                self.flock(bot, text)


    def stratHelper(self, data, meta):
        bot = self.bot[meta['bot']]
        for scrip, df in data.items():
            check = df.iloc[-1]
            if np.abs(check['Change']) >= 1:
                self.flock(bot=bot, txt='{} change: {}'.format(scrip, check['Change']))
