import os
from app import petrosa_backtesting
import logging


logging.warning('starting petrosa-usa-strategy-ta-backtesting | ver.: ' +
                os.environ.get('VERSION', '0.0.0'))


while True:
    petrosa_backtesting.continuous_run()
