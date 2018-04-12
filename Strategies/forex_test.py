import json

from Events.SignalEvent import SignalEvent
from Models.rabbitmq_publisher import Publisher
from Models.rabbitmq_subscriber import Subscriber


class TestStrategy(object):
    def __init__(self, instrument):
        self.instrument = instrument
        self.ticks = 0
        self.invested = False
        self.publisher = Publisher()
        self.subscriber = Subscriber('#.TICK')

        def consume_signal(ch, method, properties, data):
            self.calculate_signals(data.decode('utf8'))

        self.subscriber.consume(consume_signal)

    def calculate_signals(self, event):
        event = json.loads(event)

        print("Received TICK: {}", event)
        if event['type'] != 'TICK':
            return

        self.ticks += 1
        if self.ticks % 3 == 0:
            if not self.invested:
                signal = SignalEvent(self.instrument, "market", "buy")
                self.submit_signal(signal)
                self.invested = True
            else:
                signal = SignalEvent(self.instrument, "market", "sell")
                self.submit_signal(signal)
                self.invested = False

    def submit_signal(self, signal):
        signal = signal.to_json()
        print("Published Signal: {}", signal)
        self.publisher.publish(self.instrument + '.SIGNAL', signal)


if __name__ == "__main__":
    strategy = TestStrategy('EUR_USD')
