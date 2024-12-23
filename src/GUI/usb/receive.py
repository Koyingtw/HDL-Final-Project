import serial
import serial.tools.list_ports
import time
import threading
import socket
import json


class CommandSocket:
    def __init__(self, port=12346, host='localhost'):
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
            print(f"初始化命令處理程序連接: {self.host}:{self.port}")
        except Exception as e:
            self.connected = False
            print(f"無法連接到命令處理程序: {e}")
            return f"無法連接到命令處理程序: {e}"
            
    def send_command(self, type, command):
        """發送命令到其他程序"""
        print(f"發送命令到 GUI.main: {command}")
        print("Connected: ", self.connected)
        try:
            if not self.connected:
                init_result = self.init_socket()
                if not self.connected:
                    return init_result

            message = None
            if (type == 'keyboard'):
                message = {
                    'type': 'keyboard',
                    'content': command,
                    'timestamp': time.time()
                }
            elif (type == 'buy'):
                if command == '01':
                    command = 'btc'
                elif command == '02':
                    command = 'eth'
                message = {
                    'type': 'buy',
                    'content': command,
                    'timestamp': time.time()
                }
                
            elif (type == 'sell'):
                if command == '01':
                    command = 'btc'
                elif command == '02':
                    command = 'eth'
                message = {
                    'type': 'sell',
                    'content': command,
                    'timestamp': time.time()
                }
            elif (type == 'close'):
                if command == '01':
                    command = 'btc'
                elif command == '02':
                    command = 'eth'
                message = {
                    'type': 'close',
                    'content': command,
                    'timestamp': time.time()
                }
            elif (type == 'k-line'):
                if command == '01':
                    command = 'btc'
                elif command == '02':
                    command = 'eth'
                message = {
                    'type': 'k-line',
                    'content': command,
                    'timestamp': time.time()
                }
            elif (type == 'profit'):
                if command == '01':
                    command = 'btc'
                elif command == '02':
                    command = 'eth'
                message = {
                    'type': 'profit',
                    'content': command,
                    'timestamp': time.time()
                }
            
            print(f"發送命令給 GUI: {message}")
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
            
class UART: 
    state = 0
    cnt = 0
    buffer = []
    command_socket = None
    def __init__(self, GUI = None):
        self.GUI = GUI
        self.state = 0
        self.cnt = 0
        self.buffer = []
        self.command_socket = CommandSocket()
        self.ser = None
        self.is_running = True
        # self.uart_communication()
        comm_thraed = threading.Thread(target=self.uart_communication, daemon=True)
        comm_thraed.start()
        print("初始化 UART 通訊")

    def find_usb_port(self):
        ports = list(serial.tools.list_ports.comports())
        for port in ports:
            if 'usb' in port.device.lower():
                return port.device
        return None

    def uart_communication(self):
        port_name = self.find_usb_port()
        if not port_name:
            print("找不到 USB 串口裝置")
            return

        try:
            self.ser = serial.Serial(
                port=port_name,
                baudrate=9600,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1
            )

            print(f"成功連接到 {port_name}")

            # 建立接收和發送執行緒
            rx_thread = threading.Thread(target=self.receive_data, daemon=True)
            tx_thread = threading.Thread(target=self.send_data_loop, daemon=True)

            rx_thread.start()
            tx_thread.start()

            # 等待執行緒結束
            rx_thread.join()
            tx_thread.join()

        except serial.SerialException as e:
            print(f"串口錯誤: {e}")
        finally:
            if self.ser:
                self.ser.close()

    def send_data_loop(self):
        while self.is_running:
            time.sleep(0.1)  # 避免 CPU 使用率過高
            
    def receive_data(self):
        while True:
            if self.ser.in_waiting > 0:
                data = self.ser.read()
                print(f"收到資料: {data.hex()}")
                print(int(data.hex(), 16))
                
                if self.state == 0:
                    if data.hex() == '01':
                        print("Start receiving keyboard")
                        self.state = 1
                        self.cnt = 0
                    if data.hex() == '02':
                        print("Start receiving buying signal")
                        self.state = 2
                        self.cnt = 0
                    if data.hex() == '03':
                        print("Start receiving selling signal")
                        self.state = 3
                        self.cnt = 0
                    if data.hex() == '04':
                        print("Start receiving closing signal")
                        self.state = 4
                        self.cnt = 0
                    if data.hex() == '05':
                        print("Request to get K line data")
                        self.state = 5
                        self.cnt = 0
                    if data.hex() == '06':
                        print("Request to get profit")
                        self.state = 6
                        self.cnt = 0
                elif self.state == 1:
                    print("Send command")
                    self.command_socket.send_command('keyboard', data.hex())
                    self.state = 0
                elif self.state == 2:
                    if (data.hex() == '01'):
                        print("Buy BTC")
                    elif data.hex() == '02':
                        print("Buy ETH")
                    self.command_socket.send_command('buy', data.hex())
                    self.state = 0
                elif self.state == 3:
                    if (data.hex() == '01'):
                        print("Sell BTC")
                    elif data.hex() == '02':
                        print("Sell ETH")
                    self.command_socket.send_command('sell', data.hex())
                    self.state = 0
                elif self.state == 4:
                    if (data.hex() == '01'):
                        print("Close BTC")
                    elif data.hex() == '02':
                        print("Close ETH")
                    self.command_socket.send_command('close', data.hex())
                    self.state = 0
                elif self.state == 5:
                    if (data.hex() == '01'):
                        print("Get BTC K line")
                    elif data.hex() == '02':
                        print("Get ETH K line")
                    self.command_socket.send_command('k-line', data.hex())
                    self.state = 0
                elif self.state == 6:
                    if (data.hex() == '01'):
                        print("Get BTC profit")
                    elif data.hex() == '02':
                        print("Get ETH profit")
                    self.command_socket.send_command('profit', data.hex())
                    self.state = 0
                        
                        

    def send_data(self, value, enable_print=False):
        if not self.ser:
            print("串口未初始化")
            return False
            
        try:
            # if -128 <= value <= 127:
            # 將有符號整數轉換為二補數形式的 8 位元無符號整數
            unsigned_value = value & 0xFF
            self.ser.write(bytes([unsigned_value]))
            if enable_print:
                print(f"已發送: {unsigned_value}")
            return True
            # else:
            #     print("請輸入 -128 到 127 之間的數字")
            #     return False
        except ValueError:
            print("請輸入有效的數字")
            return False
                

def main():
    uart = UART()

if __name__ == "__main__":
    main()