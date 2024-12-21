import os
from binance.client import Client
from binance.enums import *

asset_list = ['BTC', 'ETH', 'BNB', 'SOL', 'BUSD']

def market_order(client, symbol, side, quantity, leverage=100):
    symbol = symbol.upper()
    if symbol not in asset_list:
        print(f"無效的交易對: {symbol}")
        return None
    symbol = symbol + 'USDT'
    print(f"執行市價{side}單: {quantity} {symbol.upper()} x{leverage}")
    print(client.futures_change_leverage(
        symbol=symbol,
        leverage=leverage
    ))
    try:
        order = client.futures_create_order(
            symbol=symbol.upper(),
            side=side,
            type='MARKET',
            quantity=quantity
        )
        print(order)
        return order
    except Exception as e:
        print(f"下單錯誤: {e}")
        return None
    
def limit_order(client, symbol, side, quantity, price):
    try:
        order = client.futures_create_order(
            symbol=symbol.upper(),
            side=side,
            type='LIMIT',
            quantity=quantity,
            price=price
        )
        return order
    except Exception as e:
        print(f"下單錯誤: {e}")
        return e

def change_leverage(client, symbol, leverage):
    symbol = symbol.upper()
    if symbol not in asset_list:
        print(f"無效的交易對: {symbol}")
        return None
    symbol = symbol + 'USDT'
    try:
        print(result = client.futures_change_leverage(
            symbol=symbol,
            leverage=leverage
        ))
        return result
    except Exception as e:
        print(f"更改槓桿錯誤: {e}")
        return e

# market_order(symbol='BTCUSDT', side='BUY', quantity=0.005)