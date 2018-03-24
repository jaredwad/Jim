from Data.IDataHandler import IDataHandler
import pika
import pandas as pd


class ForexCSVDataHandler(IDataHandler):

    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='JIM', exchange_type='topic')

    def on_receive_data(self, data):
        # entity.provider.exchange.symbol.event
        key = 'forex.csv.csv.' + data['symbol'] + 'tick'

        self.channel.basic_publish(exchange='JIM', routing_key=key, body=data)


def read_csv(symbol='EURUSD'):
    return pd.read_csv('/Users/jared/dev/Jim/ForexData/' + symbol + '.csv'
                       , parse_dates=[['<DTYYYYMMDD>', '<TIME>']], index_col=0)


if __name__ == "__main__":
    data_handler = ForexCSVDataHandler()
    df = read_csv()

    for index, row in df.iterrows():
        data_handler.on_receive_data(row)
