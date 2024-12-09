import os
from binance.client import Client
from binance.enums import *

api_key = os.environ.get('API_KEY')
api_secret = os.environ.get('SECRET_KEY')

client = Client(api_key, api_secret)
client.API_URL = 'https://api.binance.com/api'

asset_list = ['BTC', 'BETH', 'BNB', 'SOL', 'BUSD']
for asset in asset_list:
    print(client.get_asset_balance(asset= asset))
    
symbol_list = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'BUSDUSDT']
for symbol in symbol_list:
    price = client.get_symbol_ticker(symbol=symbol)
    print(price)
    
balance = client.get_asset_balance(asset='USDT')
print(balance)


# order = client.create_order(
#     symbol='BTCUSDT',
#     side=SIDE_BUY,
#     type=ORDER_TYPE_LIMIT,
#     timeInForce=TIME_IN_FORCE_GTC,
#     quantity=0.0001,
#     price='96000')

symbol = 'BTCUSDT'
leverage = 100
client.futures_change_leverage(symbol=symbol, leverage=leverage)

# 設定保證金類型為ISOLATED(逐倉)
# client.futures_change_margin_type(symbol=symbol, marginType='ISOLATED')

def place_futures_order(symbol, side, quantity):
    try:
        order = client.futures_create_order(
            symbol=symbol,
            side=side,
            type='MARKET',
            quantity=quantity
        )
        return order
    except Exception as e:
        print(f"下單錯誤: {e}")
        return None
    
place_futures_order(symbol='BTCUSDT', side='BUY', quantity=0.005)