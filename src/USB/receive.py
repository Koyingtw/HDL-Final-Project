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
            
    def send_command(self, command):
        """發送命令到其他程序"""
        print(f"發送命令: {command}")
        print(self.connected)
        try:
            if not self.connected:
                init_result = self.init_socket()
                if not self.connected:
                    return init_result
                
            message = {
                'type': 'keyboard',
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


def find_usb_port():
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        if 'usb' in port.device.lower():
            return port.device
    return None

def uart_communication():
    port_name = find_usb_port()
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
                    global state
                    global cnt
                    global buffer
                    global command_socket
                    if state == 0:
                        if data.hex() == '01':
                            print("Start receiving keyboard")
                            state = 1
                            cnt = 0
                    elif state == 1:
                        print("Send command")
                        command_socket.send_command(data.hex())
                        state = 0
                            
                            

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

if __name__ == "__main__":
    global command_socket
    global state
    global cnt
    # state = 0: Waiting
    # state = 1: Receiving keyboard
    global buffer

    state = 0
    cnt = 0
    buffer = []
    command_socket = CommandSocket()
    time.sleep(1)
    command_socket.send_command('01')

    uart_communication()