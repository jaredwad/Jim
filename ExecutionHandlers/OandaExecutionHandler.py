import datetime
import json

import v20
import settings
from Events.FillEvent import FillEvent
from Events.OrderEvent import OrderEvent
from Events.rabbitmq_publisher import Publisher
from Events.rabbitmq_subscriber import Subscriber
from ExecutionHandlers.IExecutionHandler import IExecutionHandler


class OandaExecutionHandler(IExecutionHandler):

    def __init__(self, is_practice=True):
        self.publisher = Publisher()

        DOMAIN = 'practice'
        if not is_practice:
            DOMAIN = 'real'

        self.api = v20.Context(
            settings.ENVIRONMENTS["api"][DOMAIN],
            ssl=True,
            token=settings.ACCESS_TOKEN,
            datetime_format="RFC3339"
        )

        self.subscriber = None

    def subscribe(self):
        self.subscriber = Subscriber('#.ORDER')

        def consume_signal(ch, method, properties, data):
            self.execute_order(json.loads(data.decode('utf8')))

        print('Listening for Orders...')

        self.subscriber.consume(consume_signal)

    def execute_order(self, order_event):
        print('Recieved ORDER: ', order_event)

        order_event = OrderEvent.from_json(order_event)

        direction = 1 if order_event.side.lower() == 'buy' else -1
        quantity = order_event.units
        instrument = order_event.instrument

        print("Bought {0} shares of {1}".format(quantity, instrument))

        price = self.submit_order(instrument, quantity * direction)

        fill_event = FillEvent(
            datetime.datetime.utcnow(), instrument,
            'Oanda', quantity, direction, price)

        self.publisher.publish('{0}.FILL'.format(instrument), fill_event.to_json())

    def submit_order(self, symbol, quantity):
        print('Submitting Order: {0}, {1}'.format(symbol, quantity))
        response = self.api.order.market(
            settings.ACCOUNT_ID,
            instrument=symbol,
            units=quantity)

        return response.get('orderFillTransaction').price


if __name__ == "__main__":
    executor = OandaExecutionHandler()

    executor.subscribe()
