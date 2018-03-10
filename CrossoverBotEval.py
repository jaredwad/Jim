from oandapyV20.contrib.factories import InstrumentsCandlesFactory
from oandapyV20 import API

from Bots.CrossoverBot import CrossoverBot

OANDA_ACCESS_TOKEN = 'f9b5dd551d7338502d934493c54e8017-97090cad369886b74acde0ce63f00b04'
OANDA_ACCOUNT_ID = '101-001-7607931-001'

client = API(access_token=OANDA_ACCESS_TOKEN)

instr = "EUR_USD"

params = {
    "granularity": "M1",
    "from": "2012-01-01T00:00:00Z",
    "to": "2017-06-30T00:00:00Z"
}

bot = CrossoverBot()


def cnv(r):
    for candle in r.get('candles'):
        ctime = candle.get('time')[0:19]
        try:
            rec = "{time},{complete},{o},{h},{l},{c},{v}".format(
                time=ctime,
                complete=candle['complete'],
                o=candle['mid']['o'],
                h=candle['mid']['h'],
                l=candle['mid']['l'],
                c=candle['mid']['c'],
                v=candle['volume'],
            )

            close = float(candle['mid']['c'])

            bot.tick(close)

        except Exception as e:
            print(e, r)
        else:
            # print(rec + "\n")
            print("Current Price: " + str(close) + " Current Value: " + str(bot.get_current_value()))


for r in InstrumentsCandlesFactory(instrument=instr, params=params):
    print("REQUEST: {} {} {}".format(r, r.__class__.__name__, r.params))
    rv = client.request(r)
    cnv(r.response)
