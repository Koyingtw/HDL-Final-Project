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
        print(f"發送命令: {command}")
        print(self.connected)
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
                print(message)
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
                print(message)
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
                print(message)
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
                print(message)
            
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
        self.uart_communication()

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
            ser = serial.Serial(
                port=port_name,
                baudrate=9600,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1
            )

            print(f"成功連接到 {port_name}")

            def receive_data():
                while True:
                    if ser.in_waiting > 0:
                        data = ser.read()
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
                                
                                

            def send_data():
                while True:
                    try:
                        user_input = input("請輸入要發送的數字 (0-255): ")
                        value = int(user_input)
                        if 0 <= value <= 255:
                            ser.write(bytes([value]))
                            print(f"已發送: {value}")
                        else:
                            print("請輸入 0-255 之間的數字")
                    except ValueError:
                        print("請輸入有效的數字")

            # 建立接收和發送執行緒
            rx_thread = threading.Thread(target=receive_data, daemon=True)
            tx_thread = threading.Thread(target=send_data, daemon=True)

            rx_thread.start()
            tx_thread.start()

            # 等待執行緒結束
            rx_thread.join()
            tx_thread.join()

        except serial.SerialException as e:
            print(f"串口錯誤: {e}")
        finally:
            if 'ser' in locals():
                ser.close()
                

def main():
    uart = UART()

if __name__ == "__main__":
    main()