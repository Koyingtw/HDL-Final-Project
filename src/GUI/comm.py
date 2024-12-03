import socket
import time
import json

class CommandSocket:
    def __init__(self, port=12345, host='localhost'):
        self.port = port
        self.host = host
        self.socket = None
        self.connected = False
        self.init_socket()
        
    def init_socket(self):
        """初始化命令發送socket"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
        except Exception as e:
            self.connected = False
            return f"無法連接到命令處理程序: {e}"
            
    def send_command(self, command):
        """發送命令到其他程序"""
        try:
            if not self.connected:
                init_result = self.init_socket()
                if not self.connected:
                    return init_result
                
            message = {
                'type': 'command',
                'content': command,
                'timestamp': time.time()
            }
            
            self.socket.send(json.dumps(message).encode())
            return None
            
        except Exception as e:
            self.connected = False
            self.socket = None
            return f"發送命令失敗: {e}"
    
    def close(self):
        """關閉socket連接"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
            self.connected = False

class CommandReceiver:
    def __init__(self, port=12346):
        self.port = port
        self.running = True
        
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
        # 例如：
        # if command.startswith('start'):
        #     # 處理啟動命令
        # elif command.startswith('stop'):
        #     # 處理停止命令
        
    def stop(self):
        """停止服務器"""
        self.running = False
