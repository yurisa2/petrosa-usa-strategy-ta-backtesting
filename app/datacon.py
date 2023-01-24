import datetime
import logging
import os
import random

import newrelic.agent
import pandas as pd
import pymongo


@newrelic.agent.background_task()
def get_client() -> pymongo.MongoClient:
    client = pymongo.MongoClient(
        os.getenv(
            'MONGO_URI', 'mongodb://root:QnjfRW7nl6@localhost:27017'),
        readPreference='secondaryPreferred',
        appname='petrosa-usa-ta-backtesting'
    )

    return client


def get_data(ticker, period, limit=999999999):

    suffix = period

    client = get_client()
    db = client["petrosa_usa"]
    history = db["candles_" + suffix]

    results = history.find({'ticker': ticker},
                           sort=[('datetime', -1)]).limit(limit)
    results_list = list(results)

    if (len(results_list) == 0):
        return []

    data_df = pd.DataFrame(results_list)

    data_df = data_df.sort_values("datetime")

    data_df = data_df.rename(columns={"open": "Open",
                                      "high": "High",
                                      "low": "Low",
                                      "close": "Close"}
                             )

    data_df = data_df.set_index('datetime')

    return data_df


@newrelic.agent.background_task()
def find_params():
    client = get_client()
    try:
        params = client.petrosa_usa['backtest_controller'].find(
            {"status": 0, "str_class": "ta"})
        params = list(params)

        if len(params) == 0:
            params = client.petrosa_usa['backtest_controller'].find(
                {"status": 1, "str_class": "ta"})
            params = list(params)

        if len(params) == 0:
            params = client.petrosa_usa['backtest_controller'].find(
                {"str_class": "ta"})
            params = list(params)

        if len(params) == 1:
            params = params[0]
        elif len(params) == 0:
            raise Exception("No params found, check DB")
        else:
            params = params[random.randint(0, len(params))]

        client.petrosa_usa['backtest_controller'].update_one(
            params, {"$set": {"status": 1}})
    except Exception as e:
        logging.error(e)
        raise

    return params


@newrelic.agent.background_task()
def update_status(params, status):
    client = get_client()

    client.petrosa_usa['backtest_controller'].update_one(
        {"_id": params['_id']}, {"$set": {"status": status}})

    return True


@newrelic.agent.background_task()
def post_results(symbol, test_period, doc, strategy):
    client = get_client()
    client.petrosa_usa['backtest_results'].delete_one({"strategy": strategy,
                                                          "symbol": symbol,
                                                          "period": test_period
                                                          })
    client.petrosa_usa['backtest_results'].update_one(
        {"strategy": strategy,
         "symbol": symbol,
         "period": test_period
         }, {"$set": doc}, upsert=True)
    return True


@newrelic.agent.background_task()
def post_list_results(symbol, test_period, doc, strategy):
    client = get_client()

    client.petrosa_usa['backtest_results_lists'].delete_one({"strategy": strategy,
                                                          "symbol": symbol,
                                                          "period": test_period
                                                          })

    client.petrosa_usa['backtest_results_lists'].update_one(
        {"strategy": strategy,
         "symbol": symbol,
         "period": test_period
         }, {"$set": doc}, upsert=True)
    return True


def json_to_df(candles_list) -> pd.DataFrame:

    dat = pd.DataFrame(candles_list)
    dat['datetime'] = dat['datetime'].sort_values(ascending=False)

    dat = dat.sort_values(['datetime'], ignore_index=True)

    return dat


def screening_output(
    ticker,
    timeframe,
    pet_datetime,
    entry_value,
    disruption_value,
    stop_loss,
    take_profit,
    direction
):

    if (timeframe == 'm15'):
        minutes = 15
    elif (timeframe == 'm30'):
        minutes = 30
    elif (timeframe == 'h1'):
        minutes = 60
    else:
        raise

    valid_until = pet_datetime + datetime.timedelta(minutes=minutes)

    ret = {}
    ret['ticker'] = ticker
    ret['datetime'] = pet_datetime
    ret['entry_value'] = entry_value
    ret['disruption_value'] = disruption_value
    ret['stop_loss'] = stop_loss
    ret['take_profit'] = take_profit
    ret['direction'] = direction
    ret['timeframe'] = timeframe
    ret['valid_until'] = valid_until

    return ret
