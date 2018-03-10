import v20
from datetime import datetime, timedelta

OANDA_ACCESS_TOKEN = 'f9b5dd551d7338502d934493c54e8017-97090cad369886b74acde0ce63f00b04'
OANDA_ACCOUNT_ID = '101-001-7607931-001'


def main():
    print("------ System online -------", datetime.now())
    latest_price_time = (datetime.utcnow() - timedelta(seconds=15)).isoformat('T') + 'Z'

    api = v20.Context(
        'api-fxpractice.oanda.com',
        '443',
        token=OANDA_ACCESS_TOKEN)

    response = api.pricing.get(
        OANDA_ACCOUNT_ID,
        instruments='EUR_USD',
        since=latest_price_time,
        includeUnitsAvailable=False)

    print(response.reason + latest_price_time)

    prices = response.get("prices", 200)
    if len(prices):
        buy_price = prices[0].bids[0].price

        print("Buy at " + str(buy_price))

        response = api.order.market(
            OANDA_ACCOUNT_ID,
            instrument='EUR_USD',
            units=5000)

        print("Trading id: " + str(response.get('orderFillTransaction').id))
        print("Account Balance: " + str(response.get('orderFillTransaction').accountBalance))
        print("Price: " + str(response.get('orderFillTransaction').price))

    else:
        print(response.reason)


if __name__ == "__main__":
    main()
