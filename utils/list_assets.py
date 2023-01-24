import os
import tickerlist
import pymongo

client = pymongo.MongoClient(
            os.getenv(
                'MONGO_URI', 'mongodb://root:QnjfRW7nl6@localhost:27017'),
            readPreference='secondaryPreferred',
            appname='petrosa-manual'
                                    )

full_bt_list = []

for symbol in tickerlist.asset_list:
    row = {}
    row['Symbol'] = symbol
    full_bt_list.append(row)


print(full_bt_list)
res = client.petrosa_usa['ticket_list'].insert_many(full_bt_list, ordered=False)