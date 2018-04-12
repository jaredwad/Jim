import v20
import settings
from DataHandlers.IDataHandler import IDataHandler
from Events.TickEvent import TickEvent
from Models.rabbitmq_publisher import Publisher


class OandaDataHandler(IDataHandler):

    def __init__(self, is_practice=True):
        self.publisher = Publisher()

        DOMAIN = 'practice'
        if not is_practice:
            DOMAIN = 'real'

        self.api = v20.Context(
            settings.ENVIRONMENTS["streaming"][DOMAIN],
            ssl=True,
            token=settings.ACCESS_TOKEN,
            datetime_format="RFC3339"
        )

        self.cur_bid = None
        self.cur_ask = None

    def start_stream(self):
        response = self.api.pricing.stream(
            settings.ACCOUNT_ID,
            # snapshot=True,
            instruments='EUR_USD',
        )

        for msg_type, msg in response.parts():
            if msg_type == "pricing.PricingHeartbeat":
                print(heartbeat_to_string(msg))
                self.on_recieve_heartbeat(msg.time)
            elif msg_type == "pricing.Price":
                tick = TickEvent(msg.instrument, msg.time
                                 , [{'price': bid.price, 'liquidity': bid.liquidity} for bid in msg.bids]
                                 , [{'price': ask.price, 'liquidity': ask.liquidity} for ask in msg.asks])
                self.cur_bid = tick.current_bid_price()
                self.cur_ask = tick.current_ask_price()
                print(price_to_string(tick))
                self.on_receive_data(tick)

    def on_recieve_heartbeat(self, time):
        self.publisher.publish('EUR.USD.HEARTBEAT', '{type: "HEARTBEAT", time: ' + time + '}')

    def on_receive_data(self, tick):
        self.publisher.publish('EUR_USD.TICK', tick.to_json())


def price_to_string(price):
    return "{}   ({}) {}/{}".format(
        price.instrument,
        price.time,
        price.bids,
        price.asks
    )


def heartbeat_to_string(heartbeat):
    return "HEARTBEAT ({})".format(
        heartbeat.time
    )


if __name__ == "__main__":
    oanda = OandaDataHandler()
    oanda.start_stream()
