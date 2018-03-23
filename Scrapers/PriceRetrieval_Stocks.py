#!/usr/bin/python
# -*- coding: utf-8 -*-

# price_retrieval.py

from __future__ import print_function

import datetime
import time
import warnings

import MySQLdb as mdb
import quandl
import requests

quandl.ApiConfig.api_key = '62Y-M_LfdyDYU2mZ26Hz'

# Obtain a database connection to the MySQL instance
db_host = '0.0.0.0'
db_user = 'root'
db_pass = 'jaredCocobear1&'
db_name = 'Securities_Master'
con = mdb.connect(db_host, db_user, db_pass, db_name)


def obtain_list_of_db_tickers():
    """
    Obtains a list of the ticker symbols in the database.
    """
    with con:
        cur = con.cursor()
        cur.execute("SELECT id, ticker FROM symbol")
        data = cur.fetchall()
        return [(d[0], d[1]) for d in data]


def get_daily_historic_data_quandl(
        ticker, start_date=(2012, 1, 1),
        end_date=datetime.date.today().timetuple()[0:3]
):
    """
    Obtains data from quandl and returns a list of tuples.

    ticker: Ticker symbol, e.g. "GOOG" for Google, Inc.
    start_date: Start date in (YYYY, M, D) format
    end_date: End date in (YYYY, M, D) format
    """
    start_date = datetime.date(*start_date)

    if end_date:
        end_date = datetime.date(*end_date)
    else:
        end_date = datetime.date.today()

    # Try connecting to Quandl and obtaining the data
    # On failure, print an error message.
    while True:
        prices = []
        try:
            df = quandl.get('WIKI/' + ticker,
                            returns='pandas',
                            start_date=start_date,
                            end_date=end_date,
                            collapse='daily',
                            order='asc'
                            )
            df = df.loc[:, ['Open', 'High', 'Low', 'Close', 'Adj. Close', 'Volume']]
            tmp_prices = df.reset_index().values
            for p in tmp_prices:
                prices.append(
                    (p[0].to_pydatetime(),
                     p[1], p[2], p[3]
                     , p[4], p[6], p[5])
                )
        except quandl.LimitExceededError as e:
            print("Rate Limit exceeded, waiting for 5 Minutes...")
            time.sleep(300)
            continue
        except Exception as e:
            print("Could not download data for symbol {0}: {1}".format(ticker, e))

        break

    return prices


def insert_daily_data_into_db(
        data_vendor_id, symbol_id, daily_data
):
    """
    Takes a list of tuples of daily data and adds it to the
    MySQL database. Appends the vendor ID and symbol ID to the data.

    daily_data: List of tuples of the OHLC data (with
    adj_close and volume)
    """
    # Create the time now
    now = datetime.datetime.utcnow()

    # Amend the data to include the vendor ID and symbol ID
    daily_data = [
        (data_vendor_id, symbol_id, d[0], now, now,
         d[1], d[2], d[3], d[4], d[5], d[6])
        for d in daily_data
    ]

    # Create the insert strings
    column_str = """data_vendor_id, symbol_id, price_date, created_date, 
                 last_updated_date, open_price, high_price, low_price, 
                 close_price, volume, adj_close_price"""
    insert_str = ("%s, " * 11)[:-2]
    final_str = "INSERT INTO daily_price (%s) VALUES (%s)" % \
                (column_str, insert_str)

    # Using the MySQL connection, carry out an INSERT INTO for every symbol
    with con:
        cur = con.cursor()
        cur.executemany(final_str, daily_data)


if __name__ == "__main__":
    # This ignores the warnings regarding Data Truncation
    # from the Quandl precision to Decimal(19,4) datatypes
    warnings.filterwarnings('ignore')

    # Loop over the tickers and insert the daily historical
    # data into the database
    tickers = obtain_list_of_db_tickers()
    lentickers = len(tickers)
    for i, t in enumerate(tickers):
        if t[1] != 'VZ':
            continue

        print(
            "Adding data for %s: %s out of %s" %
            (t[1], i + 1, lentickers)
        )
        yf_data = get_daily_historic_data_quandl(t[1])
        insert_daily_data_into_db('1', t[0], yf_data)
    print("Successfully added Quandl pricing data to DB.")
