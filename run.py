import queue
import time
from queue import Queue

from Data.HistoricCsvDataHandler import HistoricCSVIDataHandler
from ExecutionHandlers.SimulatedExicutionHandler import SimulatedExecutionHandler
from Portfolios.NaivePortfolio import NaivePortfolio
from Strategies.BuyAndHoldStrategy import BuyAndHoldStrategy

events = Queue()

bars = HistoricCSVIDataHandler(events, "StockData", ["AAPL"])
strategy = BuyAndHoldStrategy(bars, events)
port = NaivePortfolio(bars, events, "",)
broker = SimulatedExecutionHandler(bars, events)

while True:
    # Update the bars (specific backtest code, as opposed to live trading)
    if bars.continue_backtest:
        bars.update_bars()
    else:
        break

    # Handle the events
    while True:
        try:
            event = events.get(False)
        except queue.Empty:
            break
        else:
            if event is not None:
                if event.type == 'MARKET':
                    strategy.calculate_signals(event)
                    port.update_timeindex(event)

                elif event.type == 'SIGNAL':
                    port.update_signal(event)

                elif event.type == 'ORDER':
                    broker.execute_order(event)

                elif event.type == 'FILL':
                    port.update_fill(event)

    # 10-Minute heartbeat
    #time.sleep(10 * 60)
print(port.output_summary_stats())
