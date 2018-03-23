import quandl
import datetime

quandl.ApiConfig.api_key = '62Y-M_LfdyDYU2mZ26Hz'


def quandl_stocks_string(symbol, start_date=(2017, 1, 1), end_date=None):
    """
    symbol is a string representing a stock symbol, e.g. 'AAPL'

    start_date and end_date are tuples of integers representing the year, month,
    and day

    end_date defaults to the current date when None
    """

    start_date = datetime.date(*start_date)

    if end_date:
        end_date = datetime.date(*end_date)
    else:
        end_date = datetime.date.today()

    return quandl_stocks(symbol, start_date, end_date)


def quandl_stocks(symbol, start_date, end_date=None):
    """
    symbol is a string representing a stock symbol, e.g. 'AAPL'

    start_date and end_date are datetimes

    end_date defaults to the current date when None
    """

    if end_date is None:
        end_date = datetime.date.today()

    return quandl.get('WIKI/' + symbol,
                      returns='pandas',
                      start_date=start_date,
                      end_date=end_date,
                      collapse='daily',
                      order='asc'
                      )


if __name__ == '__main__':
    apple_data = quandl_stocks('MMM')
    print(apple_data)
