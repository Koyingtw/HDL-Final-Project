import os
from binance.client import Client
from binance.enums import *
from .balance import *
import socket
import json
import threading
from .order import *
import time

api_key = os.environ.get('API_KEY')
api_secret = os.environ.get('SECRET_KEY')

client = Client(api_key, api_secret)
client.API_URL = 'https://api.binance.com/api'

# print(balance.get_balance())

class CommandReceiver:
    gui = None
    def __init__(self, port=12345, gui=None):
        self.port = port
        self.running = True
        self.gui = gui
        
    def start_server(self):
        """啟動命令接收服務器"""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('localhost', self.port))
        server.listen(5)
        print(f"命令接收服務器啟動在端口 {self.port}")
        
        while self.running:
            try:
                client, addr = server.accept()
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client,),
                    daemon=True
                )
                client_thread.start()
            except Exception as e:
                print(f"服務器錯誤: {e}")
                
    def handle_client(self, client):
        """處理客戶端連接"""
        try:
            while self.running:
                data = client.recv(1024)
                if not data:
                    break
                try:
                    message = json.loads(data.decode())
                    self.process_command(message)
                except json.JSONDecodeError:
                    print("無效的JSON格式")
                    
        except Exception as e:
            print(f"客戶端處理錯誤: {e}")
        finally:
            client.close()
            
    def process_command(self, message):
        """處理接收到的命令"""
        if message['type'] == 'command':
            command = message['content']
            print(f"API 收到命令: {command}")
            # 在這裡處理您的命令
            self.execute_command(command)
            
    def execute_command(self, command):
        """執行命令的具體邏輯"""
        # 這裡實現您的命令處理邏輯
        print(f"API 執行命令: {command}")
        if command['command'] == 'market-buy':
            print(f"市價買入: {command['args']['symbol']} {command['args']['amount']}")
            market_order(client, symbol=command['args']['symbol'], side='BUY', quantity=command['args']['amount'])
        elif command['command'] == 'market-sell':
            print(f"市價賣出: {command['args']['symbol']} {command['args']['amount']}")
            market_order(client, symbol=command['args']['symbol'], side='SELL', quantity=command['args']['amount'])
        elif command['command'] == 'limit-buy':
            print(f"限價買入: {command['args']['symbol']} {command['args']['amount']} {command['args']['price']}")
            limit_order(client, symbol=command['args']['symbol'], side='BUY', quantity=command['args']['amount'], price=command['args']['price'])
        elif command['command'] == 'limit-sell':
            print(f"限價賣出: {command['args']['symbol']} {command['args']['amount']} {command['args']['price']}")
            limit_order(client, symbol=command['args']['symbol'], side='SELL', quantity=command['args']['amount'], price=command['args']['price'])
        elif command['command'] == 'close-position':
            print(f"平倉: {command['args']['symbol']}")
            close_position(client, symbol=command['args']['symbol'])
        elif command['command'] == 'query':
            print(f"查詢賬戶")
            self.gui.update_log(get_balance(client=client))
        elif command['command'] == 'query-info':
            data = get_balance(client=client).split('\n')
            # data = data[3]
            print(data)
            import json
            if (data[3] != ''):
                position_data = json.loads(data[3].replace("'", '"'))
                self.gui.position = position_data['positionAmt']
                self.gui.trading_pair = position_data['symbol']
                self.gui.trading_price = position_data['entryPrice']
                self.gui.now_price = position_data['markPrice']
                self.gui.pnl = position_data['unRealizedProfit']
                self.gui.balance = data[0]
            else:
                self.gui.position = 'None'
                self.gui.trading_pair = 'None'
                self.gui.trading_price = 'None'
                self.gui.now_price = 'None'
                self.gui.pnl = 'None'
                self.gui.balance = data[0]
            
            self.gui.update_dashboard()
        elif command['command'] == 'change-leverage':
            print(f"更改槓桿: {command['args']['symbol']} {command['args']['leverage']}")
            change_leverage(client, symbol=command['args']['symbol'], leverage=command['args']['leverage'])
        elif command['command'] == 'k-line':        
            print("FPGA 取得 K 線資料")
            data_list = get_klines(client, symbol=command['args']['symbol'])
            try:
                # 發送起始信號
                self.gui.uart.send_data(1)
                time.sleep(0.001)  # 小延遲確保接收端準備好
                
                print("K 線資料：", data_list)
                
                # 處理每個 K 線資料
                for kline in data_list:
                    # 發送時間戳 (8 bit)
                    self.gui.uart.send_data(kline[0])                     
                    time.sleep(0.001)
                    
                    # 處理其他 24 bit 數據
                    for value in kline[1:]:
                        # 發送高 8 位
                        high_byte = (value >> 16) & 0xFF
                        # print(f"準備發送: {high_byte}")
                        self.gui.uart.send_data(high_byte)
                        time.sleep(0.001)
                        
                        # 發送中間 8 位
                        middle_byte = (value >> 8) & 0xFF
                        # print(f"準備發送: {middle_byte}")
                        self.gui.uart.send_data(middle_byte)
                        time.sleep(0.001)
                        
                        # 發送低 8 位
                        low_byte = value & 0xFF
                        # self.ser.write(bytes([low_byte]))
                        # print(f"準備發送: {low_byte}")
                        self.gui.uart.send_data(low_byte)
                        time.sleep(0.001)
                        
                return True
                
            except Exception as e:
                print(f"發送資料時發生錯誤: {e}")
                return False
        elif command['command'] == 'profit':
            print("FPGA 取得盈虧資料")
            profit_percent = get_profit_percent(client, symbol=command['args']['symbol'])
            self.gui.uart.send_data(2)
            time.sleep(0.001)
            print("profit_percent:", profit_percent)
            self.gui.uart.send_data(profit_percent, True)
            # self.gui.uart.send_data(-20)
            
            
            
            
        
    def stop(self):
        """停止服務器"""
        self.running = False
        
def main(gui=None):
    receiver = CommandReceiver(gui=gui)
    try:
        receiver.start_server()
    except KeyboardInterrupt:
        receiver.stop()
        print("服務器已停止")

# 啟動接收端服務器
if __name__ == "__main__":
    main()