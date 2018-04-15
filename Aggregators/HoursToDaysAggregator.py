import json
import pandas as pd

import numpy as np

from Events.CandleEvent import CandleEvent
from Models.rabbitmq_publisher import Publisher
from Models.rabbitmq_subscriber import Subscriber


class HoursToDaysAggregator:
    def __init__(self):
        self.data = dict()
        self.publisher = Publisher()
        self.subscriber = None

    def subscribe(self):
        self.subscriber = Subscriber('#.H1.TICK')
        print('Listening for Candles...')

        def consume_signal(ch, method, properties, data):
            candle = json.loads(data.decode('utf8'))
            self.consume_hour(CandleEvent.from_json(candle))

        self.subscriber.consume(consume_signal)

    def consume_hour(self, hour_candle):
        print(hour_candle.to_json())
        instrument = hour_candle.instrument
        if instrument not in self.data:
            self.data[instrument] = []

        if self.should_emit(hour_candle):
            self.emit_data(instrument)
            self.data[instrument] = []

        self.data[instrument].append(hour_candle)

    def should_emit(self, hour_candle):
        data = self.data[hour_candle.instrument]
        return data and data[0].time.day != hour_candle.time.day

    def emit_data(self, instrument):
        data = self.combine_candles(instrument)

        print('EMITTING: ' + data.to_json())

        self.publisher.publish(instrument + '.' + 'D1.TICK', data.to_json())
        pass

    def combine_candles(self, instrument):
        data = self.data[instrument]

        open = data[0].candle.open
        close = data[-1].candle.close
        high = np.max([item.candle.high for item in data])
        low = np.min([item.candle.low for item in data])
        volume = np.sum([item.volume for item in data])

        return CandleEvent(instrument, data[-1].time, 'D1', open, high, low, close, volume)


if __name__ == "__main__":
    oanda = HoursToDaysAggregator()
    oanda.subscribe()
