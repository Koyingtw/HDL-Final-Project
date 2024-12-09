def get_balance(client):
    data = ""
    asset_list = ['USDT']
    balance = client.futures_account_balance()
    for asset in balance:
        if asset['asset'] in asset_list:
            print(asset['asset'], asset['balance'], sep=': ')
            data += f"{asset['asset']}: {asset['balance']}\n"
        
    positions = client.futures_position_information()
    
    
    print("---")
    data += "---\n"
    print("持倉資訊")
    data += "持倉資訊\n"

    for position in positions:
        print(position)
        data += f"{position}\n"
        if float(position['positionAmt']) != 0:
            print(f"持倉數量: {position['positionAmt']} {position['symbol']}")
            data += f"持倉數量: {position['positionAmt']} {position['symbol']}\n"
            print(f"入場價格: {position['entryPrice']}")
            data += f"入場價格: {position['entryPrice']}\n"
            print(f"未實現盈虧: {position['unRealizedProfit']} USDT")
            data += f"未實現盈虧: {position['unRealizedProfit']} USDT\n"
            print(f"保證金: {position['maintMargin']} USDT")
            data += f"保證金: {position['maintMargin']} USDT\n"
            # print(f"槓桿: {position['leverage']} 倍")
            tp_sl_orders = client.futures_get_open_orders(symbol=position['symbol'])
        
            for order in tp_sl_orders:
                # print(order)
                if order['type'] == 'TAKE_PROFIT_MARKET':
                    print(f"止盈價格：{order['stopPrice']}")
                    data += f"止盈價格：{order['stopPrice']}\n"
                elif order['type'] == 'STOP_MARKET':
                    print(f"止損價格：{order['stopPrice']}")
                    data += f"止損價格：{order['stopPrice']}\n"
            print("---")
            data += "---\n"
    return data