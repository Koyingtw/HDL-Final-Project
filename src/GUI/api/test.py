from binance.spot import Spot
import os
import logging
from binance.spot import Spot as Client
from binance.lib.utils import config_logging
from examples.utils.prepare_env import get_api_key

api_key = os.environ.get('API_KEY')
api_secret = os.environ.get('SECRET_KEY')
client = Spot(api_key, api_secret)


config_logging(logging, logging.DEBUG)

spot_client = Client(api_key, api_secret)
logging.info(spot_client.balance())