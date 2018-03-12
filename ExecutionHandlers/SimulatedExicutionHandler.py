import datetime

from Events.FillEvent import FillIEvent
from ExecutionHandlers.IExecutionHandler import IExecutionHandler


class SimulatedExecutionHandler(IExecutionHandler):
    """
    The simulated execution handler simply converts all order
    objects into their equivalent fill objects automatically
    without latency, slippage or fill-ratio issues.

    This allows a straightforward "first go" test of any strategy,
    before implementation with a more sophisticated execution
    handler.
    """

    def __init__(self, bars, events):
        """
        Initialises the handler, setting the event queues
        up internally.

        Parameters:
        bars - The DataHandler
        events - The Queue of Event objects.
        """
        self.bars = bars
        self.events = events

    def execute_order(self, event):
        """
        Simply converts Order objects into Fill objects naively,
        i.e. without any latency, slippage or fill ratio problems.

        Parameters:
        event - Contains an Event object with order information.
        """
        if event.type == 'ORDER':
            cost = self.bars.get_latest_bars(event.symbol)[0][5]

            fill_event = FillIEvent(datetime.datetime.utcnow(), event.symbol,
                                   'ARCA', event.quantity, event.direction, cost)
            self.events.put(fill_event)
