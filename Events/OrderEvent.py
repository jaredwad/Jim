import json

from Events.IEvent import IEvent


class OrderEvent(IEvent):
    """
    Handles the event of sending an Order to an execution system.
    The order contains a symbol (e.g. GOOG), a type (market or limit),
    quantity and a direction.
    """

    def __init__(self, instrument, units, order_type, side):
        self.type = 'ORDER'
        self.instrument = instrument
        self.units = units
        self.order_type = order_type
        self.side = side

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)

    @staticmethod
    def from_json(data):
        return OrderEvent(data['instrument'], data['units'], data['order_type'], data['side'])

        # def __init__(self, symbol, order_type, quantity, direction):
    #     """
    #     Initialises the order type, setting whether it is
    #     a Market order ('MKT') or Limit order ('LMT'), has
    #     a quantity (integral) and its direction ('BUY' or
    #     'SELL').
    #
    #     TODO: Must handle error checking here to obtain
    #     rational orders (i.e. no negative quantities etc).
    #
    #     Parameters:
    #     symbol - The instrument to trade.
    #     order_type - 'MKT' or 'LMT' for Market or Limit.
    #     quantity - Non-negative integer for quantity.
    #     direction - 'BUY' or 'SELL' for long or short.
    #     """
    #     self.type = 'ORDER'
    #     self.symbol = symbol
    #     self.order_type = order_type
    #     self.quantity = quantity
    #     self.direction = direction

    def print_order(self):
        """
        Outputs the values within the Order.
        """
        print("Order: Symbol=%s, Type=%s, Quantity=%s, Direction=%s" %
              (self.instrument, self.order_type, self.units, self.side))
