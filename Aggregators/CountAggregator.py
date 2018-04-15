import collections
import json
import numpy as np

from Events.CandleEvent import CandleEvent
from Models.rabbitmq_publisher import Publisher
from Models.rabbitmq_subscriber import Subscriber


class CountAggregator:
    def __init__(self, count=20, granularity='D1'):
        self.data = dict()
        self.publisher = Publisher()
        self.subscriber = None
        self.count = count
        self.granularity = granularity

    def subscribe(self):
        self.subscriber = Subscriber('#.' + self.granularity + '.TICK')
        print('Listening for Candles...')

        def consume_signal(ch, method, properties, data):
            candle = json.loads(data.decode('utf8'))
            self.consume_candle(CandleEvent.from_json(candle))

        self.subscriber.consume(consume_signal)

    def consume_candle(self, hour_candle):
        print(hour_candle.to_json())
        instrument = hour_candle.instrument
        if instrument not in self.data:
            self.initialize_instrument(instrument)

        self.data[instrument].append(hour_candle)

        if len(self.data[instrument]) >= self.count:
            self.prune_instrument(instrument)
            self.emit_data(instrument)

    def prune_instrument(self, instrument):
        while len(self.data[instrument]) > self.count:
            self.data[instrument].popleft()

    def emit_data(self, instrument):
        data = self.data[instrument]

        json_data = [item.to_json() for item in data]

        json_data = json.dumps(json_data)

        print('EMITTING ({}): '.format(instrument + '.' + self.granularity + '.AGGREGATE' + str(self.count)) + json_data)

        self.publisher.publish(instrument + '.' + self.granularity + '.AGGREGATE' + str(self.count), json_data)
        pass

    def initialize_instrument(self, instrument):
        self.data[instrument] = collections.deque([])


if __name__ == "__main__":
    oanda = CountAggregator()
    oanda.subscribe()
