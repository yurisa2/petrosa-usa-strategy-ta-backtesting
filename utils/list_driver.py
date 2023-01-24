import os

import pymongo

client = pymongo.MongoClient(
            os.getenv(
                'MONGO_URI', 'mongodb://root:QnjfRW7nl6@localhost:27017'),
            readPreference='secondaryPreferred',
            appname='petrosa-manual'
                                    )


col_symbols = client.petrosa_crypto['candles_h1'].aggregate(
    [{
        "$group":
        {"_id": "$ticker"
         }}
     ])


periods = ['m15', 'm30', 'h1']


full_bt_list = []

for symbol in col_symbols:
    for period in periods:
        row = {}
        row['symbol'] = symbol['_id']
        row['period'] = period
        row['strategy'] = 'bear_trap_sell'
        row['status'] = 0
        row['str_class'] = 'ta'
        # row['type'] = 'BUY'
        row['type'] = 'SELL'
        full_bt_list.append(row)
        print(row)

client.petrosa_crypto['backtest_controller'].insert_many(full_bt_list)
