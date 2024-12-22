asset_list = ['BTC', 'ETH', 'BNB', 'SOL', 'BUSD']

def get_balance(client):
    data = ""
    asset_list = ['USDT']
    balance = client.futures_account_balance()
    for asset in balance:
        if asset['asset'] in asset_list:
            print(asset['asset'], asset['balance'], sep=': ')
            data += f"{asset['asset']}: {asset['balance']}\n"
        
    positions = client.futures_position_information()
    
    
    # print("---")
    data += "---\n"
    # print("持倉資訊")
    data += "持倉資訊\n"

    for position in positions:
        data += f"{position}\n"
        if float(position['positionAmt']) != 0:
            # print(f"持倉數量: {position['positionAmt']} {position['symbol']}")
            data += f"持倉數量: {position['positionAmt']} {position['symbol']}\n"
            # print(f"入場價格: {position['entryPrice']}")
            data += f"入場價格: {position['entryPrice']}\n"
            # print(f"未實現盈虧: {position['unRealizedProfit']} USDT")
            data += f"未實現盈虧: {position['unRealizedProfit']} USDT\n"
            # print(f"保證金: {position['maintMargin']} USDT")
            data += f"保證金: {position['maintMargin']} USDT\n"
            # print(f"槓桿: {position['leverage']} 倍")
            tp_sl_orders = client.futures_get_open_orders(symbol=position['symbol'])
        
            for order in tp_sl_orders:
                # print(order)
                if order['type'] == 'TAKE_PROFIT_MARKET':
                    # print(f"止盈價格：{order['stopPrice']}")
                    data += f"止盈價格：{order['stopPrice']}\n"
                elif order['type'] == 'STOP_MARKET':
                    # print(f"止損價格：{order['stopPrice']}")
                    data += f"止損價格：{order['stopPrice']}\n"
            print("---")
            data += "---\n"
    return data

def get_profit_percent(client, symbol):
    symbol = symbol.upper()
    if symbol not in asset_list:
        print(f"無效的交易對: {symbol}")
        return None
    symbol = symbol + 'USDT'
    
    try:
        # 獲取倉位信息
        positions = client.futures_position_information(symbol=symbol)
        
        # 檢查是否有倉位
        for position in positions:
            if float(position['positionAmt']) != 0:
                margin = float(position['initialMargin'])  # 保證金
                unrealized_profit = float(position['unRealizedProfit'])  # 未實現損益
                
                # 計算損益百分比（相對於保證金）
                if margin != 0:
                    profit_percent = (unrealized_profit / margin) * 100
                    print(f"未實現盈虧: {unrealized_profit} USDT")
                    return round(profit_percent)  # 四捨五入到整數
                    
        return 0  # 如果沒有倉位
        
    except Exception as e:
        print(f"計算損益時發生錯誤: {e}")
        return None
