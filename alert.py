from conf import Configuration

class Alerts(Configuration):

    def __init__(self):
        pass

    def priceAlerts(self, scrip, zones, template=None):
        """
        parse from yml file price alerts for scrips
        """
        pass

    def stratsAlerts(self, k, df, bot):
        text = 'got in {}'.format(k)
        bot.send_message(chat_id=1443973207, text=text)

        if df['buy'].iloc[-1] == 1:
            text = 'buy triggered for {}'.format(k)
            bot.send_message(chat_id=1443973207, text=text)
        
        if df['sell'].iloc[-1] == 1:
            text = 'sell triggered for {}'.format(k)
            self.bot['paisheeBot'].send_message(chat_id=1443973207, text=text)


    def volAlerts(self, scrip, range, timeframe):
        """
        volitility alerts
        """
        pass
