import pandas as pd
from datetime import datetime, timedelta

from oandapyV20.contrib.factories import InstrumentsCandlesFactory
from oandapyV20 import API
import settings
from DataHandlers.IDataHandler import IDataHandler
from Events.CandleEvent import CandleEvent
from Models.Duration import Duration
from Models.rabbitmq_publisher import Publisher
from time import sleep


class HistoricOandaDataHandler(IDataHandler):

    def __init__(self, is_practice=True, write_csv=False):
        self.publisher = Publisher()

        access_token = settings.ACCESS_TOKEN

        self.client = API(access_token=access_token, environment='live' if not is_practice else 'practice')

        _from = (datetime.utcnow() - timedelta(days=10000)).strftime('%Y-%m-%dT%H:%M:%SZ')
        _to = datetime.today().strftime('%Y-%m-%dT%H:%M:%SZ')
        self.granularity = 'D'
        self.instr = 'EUR_USD'

        self.params = {
            "granularity": self.granularity,
            "from": _from,
            "to": _to
        }

        self.cur_ask = None
        self.cur_bid = None

        self.data = []

    def start_stream(self):
        for r in InstrumentsCandlesFactory(instrument=self.instr, params=self.params):
            print("REQUEST: {} {} {}".format(r, r.__class__.__name__, r.params))
            rv = self.client.request(r)
            self.on_receive_data(r.response)

        d = dict(datetime=[c.time for c in self.data]
                 , open=[c.candle.open for c in self.data]
                 , high=[c.candle.high for c in self.data]
                 , low=[c.candle.low for c in self.data]
                 , close=[c.candle.close for c in self.data]
                 , volume=[c.volume for c in self.data])

        df = pd.DataFrame(data=d)

        df.to_csv('{0}_daily_very_long.csv'.format(self.instr), index=False)

    def on_recieve_heartbeat(self, time):
        self.publisher.publish('EUR.USD.HEARTBEAT', '{type: "HEARTBEAT", time: ' + time + '}')

    def on_receive_data(self, r):
        # self.publisher.publish('EUR_USD.TICK', tick.to_json())
        for candle in r.get('candles'):
            sleep(0.001)
            ctime = candle.get('time')[0:19]
            try:
                tick = CandleEvent(self.instr
                                   , ctime
                                   , self.granularity
                                   , float(candle['mid']['o'])
                                   , float(candle['mid']['h'])
                                   , float(candle['mid']['l'])
                                   , float(candle['mid']['c'])
                                   , float(candle['volume']))

                self.cur_bid = tick.current_bid_price()
                self.cur_ask = tick.current_ask_price()
            except Exception as e:
                print(e, r)
            else:
                print(tick.to_json())
                self.data.append(tick)
                self.publisher.publish(self.instr + '.' + self.granularity + '.TICK', tick.to_json())


def price_to_string(price):
    return "{}   ({}) {}/{}".format(
        price.instrument,
        price.time,
        price.bids[0],
        price.asks[0]
    )


def heartbeat_to_string(heartbeat):
    return "HEARTBEAT ({})".format(
        heartbeat.time
    )


if __name__ == "__main__":
    oanda = HistoricOandaDataHandler(write_csv=True)
    oanda.start_stream()
