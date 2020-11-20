from alert import Alerts
from conf import Configuration
from conf import Configuration
from parsers import StrategyParse
from datahandler import dataHandler


def main():
    config = Configuration()
    handle = dataHandler()
    alerts = Alerts()

    for k, v in config.modclass.items():
        parseStrats = StrategyParse(config.Strats[k], v)
        parseStrats.sock.start()

if __name__ == "__main__":
    main()