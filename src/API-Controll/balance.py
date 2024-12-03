def get_balance(client):
    asset_list = ['USDT']
    balance = client.futures_account_balance()
    for asset in balance:
        if asset['asset'] in asset_list:
            print(asset['asset'], asset['balance'], sep=': ')
        
    positions = client.futures_position_information()
    
    print("---")
    print("持倉資訊")

    for position in positions:
        print(position)
        if float(position['positionAmt']) != 0:
            print(f"持倉數量: {position['positionAmt']} {position['symbol']}")
            print(f"入場價格: {position['entryPrice']}")
            print(f"未實現盈虧: {position['unRealizedProfit']} USDT")
            print(f"保證金: {position['maintMargin']} USDT")
            # print(f"槓桿: {position['leverage']} 倍")
            tp_sl_orders = client.futures_get_open_orders(symbol=position['symbol'])
        
            for order in tp_sl_orders:
                # print(order)
                if order['type'] == 'TAKE_PROFIT_MARKET':
                    print(f"止盈價格：{order['stopPrice']}")
                elif order['type'] == 'STOP_MARKET':
                    print(f"止損價格：{order['stopPrice']}")
            print("---")