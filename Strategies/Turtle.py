import json
import threading

from Events.CandleEvent import CandleEvent
from Events.SignalEvent import SignalEvent
from Indicators.Breakout import Breakout
from Models.rabbitmq_publisher import Publisher
from Models.rabbitmq_subscriber import Subscriber
from Models.Duration import Duration
from Strategies.IStrategy import IStrategy


class Turtle(IStrategy):
    def __init__(self, instruments, duration=20, constrained=True):
        self.instruments = instruments
        self.breakouts = dict([(i, Breakout(length=duration)) for i in instruments])
        self.publisher = Publisher()
        self.subscriber = None
        self.in_market = False
        self.last_trade_profitable = dict([(i, False) for i in instruments])

    def subscribe(self):
        self.subscriber = Subscriber('#.TICK')
        print('Listening for TICKs...')

        def consume_signal(ch, method, properties, data):
            candle = CandleEvent.from_json(json.loads(data.decode('utf8')))
            self.calculate_signals(candle)

        self.subscriber.consume(consume_signal)

    def calculate_signals(self, candle_event):
        if candle_event.duration == Duration.DAY.name:
            self.process_signal(candle_event)
            self.increment_breakout(candle_event.instrument, candle_event.candle)


    def increment_breakout(self, instrument, candle):
        self.breakouts[instrument].tick(candle.close)

    def process_signal(self, candle_event):
        if self.in_market:
            signal = self.should_add_units()
        else:
            signal = self.should_enter_market(candle_event)

        if signal is not None:
            print('Entering Market: ' + signal.to_json())
            self.publisher.publish(candle_event.instrument + '.SIGNAL', signal.to_json())

    def should_enter_market(self, candle_event):
        instrument = candle_event.instrument
        breakout = self.breakouts[instrument]

        if not breakout.ready():
            return None

        if candle_event.candle.close > breakout.current_max:
            return SignalEvent(instrument, None, 'BUY')
        elif candle_event.candle.close < breakout.current_min:
            return SignalEvent(instrument, None, 'SELL')
        return None

    def should_add_units(self):
        return None


if __name__ == "__main__":
    instruments = ['EUR_USD']

    turtle1 = Turtle(instruments, duration=20, constrained=True)
    turtle2 = Turtle(instruments, duration=55, constrained=False)

    fast = threading.Thread(target=turtle1.subscribe, args=[])
    slow = threading.Thread(target=turtle1.subscribe, args=[])

    fast.start()
    slow.start()
