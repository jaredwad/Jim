import json
from datetime import datetime

import numpy as np

from Events.CandleEvent import CandleEvent
from Events.IndicatorEvent import IndicatorEvent
from Models.rabbitmq_publisher import Publisher
from Models.rabbitmq_subscriber import Subscriber


class Breakout:
    def __init__(self, length=20, breakout_granularity='D1', listen_granularity='H1'):
        self.length = length
        self.breakout_granularity = breakout_granularity
        self.listen_granularity = listen_granularity
        self.max_and_min_by_instrument = dict()
        self.subscriber = None
        self.publisher = Publisher()

    def subscribe(self):
        self.subscriber = Subscriber('#.H1.TICK')
        print('Listening for TICKs...')

        def consume_tick(ch, method, properties, data):
            candle = CandleEvent.from_json(json.loads(data.decode('utf8')))
            self.tick(candle)

        def consume_aggregate(ch, method, properties, data):
            json_data = json.loads(data.decode('utf8'))

            data = [CandleEvent.from_json(json.loads(item)).candle.close for item in json_data]

            instrument = CandleEvent.from_json(json.loads(json_data[0])).instrument

            self.compute_max_and_min(data, instrument)

        self.subscriber.consume_multiple(['#.{0}.TICK'.format(self.listen_granularity)
                                         , '#.{0}.AGGREGATE{1}'.format(self.breakout_granularity, self.length)]
                                         , [consume_tick, consume_aggregate])

    def tick(self, tick):
        print('Received TicK: {}'.format(tick.to_json()))

        instrument = tick.instrument

        if instrument not in self.max_and_min_by_instrument:
            self.max_and_min_by_instrument[instrument] = None

        close = tick.candle.close
        action = None

        if self.max_and_min_by_instrument[instrument] is None:
            print('No max or min yet...')
            return

        if close > self.max_and_min_by_instrument[instrument][0]:
            action = 'BUY'
        elif close < self.max_and_min_by_instrument[instrument][1]:
            action = 'SELL'

        if action is not None:
            self.send_signal(action, instrument)

    def send_signal(self, action, instrument):
        ind = IndicatorEvent(instrument, datetime.now(), action)

        print('Sending Signal: {0}'.format(ind.to_json()))

        self.publisher.publish(instrument + '.BREAKOUT.' + str(self.length), ind.to_json())

    def compute_max_and_min(self, data, instrument):
        max = np.max(data)
        min = np.min(data)

        self.max_and_min_by_instrument[instrument] = (max, min)

        print('Set Max to {0}, and Min to {1}'.format(max, min))


if __name__ == "__main__":
    breakout = Breakout(length=20, breakout_granularity='D1', listen_granularity='H1')

    breakout.subscribe()
