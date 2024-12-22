import os
from binance.client import Client
from binance.enums import *
from .balance import *
import socket
import json
import threading
from .order import *

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
            print(f"收到命令: {command}")
            # 在這裡處理您的命令
            self.execute_command(command)
            
    def execute_command(self, command):
        """執行命令的具體邏輯"""
        # 這裡實現您的命令處理邏輯
        print(f"執行命令: {command}")
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