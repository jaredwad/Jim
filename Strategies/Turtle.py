import json
import threading

from Events.CandleEvent import CandleEvent
from Events.IndicatorEvent import IndicatorEvent
from Events.SignalEvent import SignalEvent
from Indicators.Breakout import Breakout
from Models.rabbitmq_publisher import Publisher
from Models.rabbitmq_subscriber import Subscriber
from Models.Duration import Duration
from Strategies.IStrategy import IStrategy


class Turtle(IStrategy):
    def __init__(self, instruments, duration=20, constrained=True):
        self.instruments = instruments
        self.publisher = Publisher()
        self.subscriber = None
        self.in_market = dict([(i, False) for i in instruments])
        self.last_trade_profitable = dict([(i, False) for i in instruments])

    def subscribe(self):
        self.subscriber = Subscriber('')
        print('Listening for TICKs...')

        def consume_tick(ch, method, properties, data):
            candle = CandleEvent.from_json(json.loads(data.decode('utf8')))
            self.calculate_signals(candle)

        def consume_breakout(ch, method, properties, data):
            indicator = IndicatorEvent.from_json(json.loads(data.decode('utf8')))
            self.on_receive_breakout(indicator)

        self.subscriber.consume_multiple(['#.H1.TICK', '#.BREAKOUT.*'], [consume_tick, consume_breakout])

    def calculate_signals(self, candle_event):
        instrument = candle_event.instrument

        if instrument not in self.instruments:
            return

        if self.should_add_units(instrument):
            direction = self.calculate_add_units_direction(instrument)
            self.send_signal(instrument, direction)

        if self.should_exit(instrument):
            self.exit(instrument)

    def on_receive_breakout(self, indicator):
        instrument = indicator.instrument
        direction = indicator.value

        if instrument not in self.instruments:
            return

        if self.should_enter_market(instrument, direction):
            self.send_signal(instrument, direction)

    def send_signal(self, instrument, direction):
        self.publisher.publish(instrument + '.SIGNAL', SignalEvent(instrument, None, direction).to_json())

    def should_enter_market(self, instrument, direction):
        return True

    def should_add_units(self, instrument):
        return False

    def calculate_add_units_direction(self, instrument):
        return None

    def should_exit(self, instrument):
        if not self.in_market[instrument]:
            return False
        return False

    def exit(self, instrument):
        pass


if __name__ == "__main__":
    instruments = ['EUR_USD']

    turtle = Turtle(instruments, duration=20, constrained=True)

    turtle.subscribe()
