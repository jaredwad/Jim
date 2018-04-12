import json

from Events.IEvent import IEvent


class TickEvent(IEvent):
    def __init__(self, instrument, time, bids, asks):
        self.type = 'TICK'
        self.instrument = instrument
        self.time = time
        self.bids = bids
        self.asks = asks

    def current_bid_price(self):
        return self.bids[0]['price']

    def current_ask_price(self):
        return self.asks[0]['price']

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)

    @staticmethod
    def from_json(tick):
        return TickEvent(tick['instrument'], tick['time'], tick['bids'], tick['asks'])
