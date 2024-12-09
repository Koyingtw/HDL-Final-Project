import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import socket
import time
import json
import threading
import sys
import api.main as api

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
    app = None
    def __init__(self, port=12346, app=None):
        self.port = port
        self.running = True
        self.app = app
        
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
                print(data)
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
        if message['type'] == 'keyboard':
            try:
                command = message['content']
                print(f"收到鍵盤輸入: {command}")
                # print(int(command))
                # 在這裡處理您的命令
                if command == '08': # backspace
                    self.app.backspace()
                elif command == '7f': # delete
                    self.app.delete()
                elif command == '0d': # enter
                    self.app.process_command(None)
                elif command == '01': # UP
                    print('UP')
                    self.app.previous_command(None)
                elif command == '02': # DOWN
                    print('DOWN')
                    self.app.next_command(None)
                elif command == '03': # LEFT
                    self.app.move_cursor_left()
                elif command == '04': # RIGHT
                    self.app.move_cursor_right()
                else:
                    self.app.input_char(chr(int(command, 16)))
            except Exception as e:
                print(f"無法處理鍵盤輸入: {e}")
            
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

class TerminalGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("終端機模擬器")
        
        
        # 命令歷史紀錄
        self.command_history = [""]
        self.history_index = 0
        
        # 初始化命令socket
        self.command_socket = CommandSocket()
        
        self.receiver = CommandReceiver(app=self)
        self.receiver_thread = threading.Thread(
            target=self.receiver.start_server,
            daemon=True  # 使用 daemon=True 確保主程序結束時線程也會結束
        )
        self.receiver_thread.start()
        
        
        # 建立主要框架
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        # 新增資訊顯示區域
        self.info_frame = ttk.Frame(self.main_frame)
        self.info_frame.pack(fill=X, pady=(0, 5))
        
        # 建立資訊顯示的標籤們
        self.info_labels = {}
        
        # 第一行資訊
        info_row1 = ttk.Frame(self.info_frame)
        info_row1.pack(fill=X)
        
        labels_row1 = [
            ("symbol", "交易對：BTC/USDT"),
            ("leverage", "槓桿倍數：20x"),
            ("position", "持倉方向：多"),
        ]
        
        for key, text in labels_row1:
            label = ttk.Label(info_row1, text=text, padding=(10, 5))
            label.pack(side=LEFT, padx=5)
            self.info_labels[key] = label
        
        # 第二行資訊
        info_row2 = ttk.Frame(self.info_frame)
        info_row2.pack(fill=X)
        
        labels_row2 = [
            ("price", "當前價格：45000"),
            ("pnl", "收益：+500"),
            ("balance", "帳戶餘額：10000"),
        ]
        
        for key, text in labels_row2:
            label = ttk.Label(info_row2, text=text, padding=(10, 5))
            label.pack(side=LEFT, padx=5)
            self.info_labels[key] = label
        
        # 分隔線
        self.separator = ttk.Separator(self.main_frame, orient='horizontal')
        self.separator.pack(fill=X, pady=5)
        
        # 建立左右分隔
        self.paned = ttk.PanedWindow(self.main_frame, orient=HORIZONTAL)
        self.paned.pack(fill=BOTH, expand=True)
        
        # 左側終端機區域
        self.terminal_frame = ttk.Frame(self.paned)
        self.paned.add(self.terminal_frame, weight=2)
        
        # 歷史指令顯示區
        self.history_text = tk.Text(self.terminal_frame, height=20, width=50)
        self.history_text.pack(fill=BOTH, expand=True)
        self.history_text.config(state=DISABLED)
        
        # 指令輸入區
        self.input_frame = ttk.Frame(self.terminal_frame)
        self.input_frame.pack(fill=X, pady=(5,0))
        
        self.prompt_label = ttk.Label(self.input_frame, text="$ ")
        self.prompt_label.pack(side=LEFT)
        
        self.input_entry = ttk.Entry(self.input_frame)
        self.input_entry.pack(side=LEFT, fill=X, expand=True)
        
        # 右側日誌區域
        self.log_frame = ttk.Frame(self.paned)
        self.paned.add(self.log_frame, weight=1)
        
        self.log_text = tk.Text(self.log_frame, height=20, width=30)
        self.log_text.pack(fill=BOTH, expand=True)
        self.log_text.config(state=DISABLED)
        
        # 綁定按鍵事件
        # self.input_entry.bind('<Return>', self.process_command)
        # self.input_entry.bind('<Up>', self.previous_command)
        # self.input_entry.bind('<Down>', self.next_command)
        
        # self.input_entry.config(state='readonly')  # 使輸入框唯讀
        
        # 新增控制變數
        self.current_input = ""  # 當前輸入的文字
        self.cursor_position = 0 # 游標位置
        self.command_trigger = True  # Enter 鍵
        self.up_trigger = False      # 上鍵
        self.down_trigger = False    # 下鍵
        self.left_trigger = False    # 左鍵
        self.right_trigger = False   # 右鍵
        

    def check_triggers(self):
        """檢查觸發變數的狀態"""
        # 處理方向鍵
        if self.left_trigger:
            self.move_cursor_left()
            self.left_trigger = False
            
        if self.right_trigger:
            self.move_cursor_right()
            self.right_trigger = False
            
        if self.up_trigger:
            self.previous_command(None)
            self.up_trigger = False
            
        if self.down_trigger:
            self.next_command(None)
            self.down_trigger = False
            
        if self.command_trigger:
            self.process_command(None)
            self.command_trigger = False
        
        # 更新顯示
        self.update_input_display()
        
        # 每 100ms 檢查一次
        self.root.after(100, self.check_triggers)
    
    def update_input_display(self):
        """更新輸入框顯示"""
        self.input_entry.config(state='normal')
        self.input_entry.delete(0, tk.END)
        self.input_entry.insert(0, self.current_input)
        self.input_entry.icursor(self.cursor_position)
        # self.input_entry.config(state='readonly')
    
    def input_char(self, char):
        """輸入字符"""
        # 在游標位置插入字符
        print(f"輸入字符: {char}")
        self.current_input = (
            self.current_input[:self.cursor_position] + 
            char + 
            self.current_input[self.cursor_position:]
        )
        self.cursor_position += 1
        self.update_input_display()
    
    def backspace(self):
        """退格"""
        if self.cursor_position > 0:
            self.current_input = (
                self.current_input[:self.cursor_position-1] + 
                self.current_input[self.cursor_position:]
            )
            self.cursor_position -= 1
            self.update_input_display()
    
    def delete(self):
        """刪除"""
        if self.cursor_position < len(self.current_input):
            self.current_input = (
                self.current_input[:self.cursor_position] + 
                self.current_input[self.cursor_position+1:]
            )
            self.update_input_display()
    
    def move_cursor_left(self):
        """向左移動游標"""
        if self.cursor_position > 0:
            self.cursor_position -= 1
            self.update_input_display() 
    
    def move_cursor_right(self):
        """向右移動游標"""
        if self.cursor_position < len(self.current_input):
            self.cursor_position += 1
            self.update_input_display() 
            
    def is_number(self, s):    
        try:    # 如果能运⾏ float(s) 语句，返回 True（字符串 s 是浮点数）        
            float(s)        
            return True    
        except ValueError:  # ValueError 为 Python 的⼀种标准异常，表⽰"传⼊⽆效的参数"        
            pass  # 如果引发了 ValueError 这种异常，不做任何事情（pass：不做任何事情，⼀般⽤做占位语句）    
        try:        
            import unicodedata  # 处理 ASCII 码的包        
            unicodedata.numeric(s)  # 把⼀个表⽰数字的字符串转换为浮点数返回的函数        
            return True    
        except (TypeError, ValueError):        
            pass    
            return False
    
    def command_decode(self, command):
        symbols = ['btc', 'eth']
        commands = command.split(' ')
        print(commands)
        if (commands[0] == 'query'):
            if (commands[1] == 'account'):
                data = {
                    'command': 'query',
                    'args': 'account',
                    'timestamp': time.time()
                }
                return data
            else:
                return None
        elif (commands[0] == 'buy' or commands[0] == 'sell'):
            if (len(commands) == 3):
                if (commands[1] in symbols and self.is_number(commands[2])):
                    data = {
                        'command': 'market-' + commands[0],
                        'args': {
                            'symbol': commands[1],
                            'amount': commands[2]
                        }
                    }
                    return data
                else:
                    print('Invalid command', commands)
                    return None
            elif (len(commands) == 5 and commands[2] == 'at'):
                if (commands[1] in symbols and self.is_number(commands[3]) and self.is_number(commands[4])):
                    data = {
                        'command': 'limit-' + commands[0],
                        'args': {
                            'symbol': commands[1],
                            'price': commands[3],
                            'amount': commands[4]
                        }
                    }
                    return data
            else:
                return None
        
    
    def process_command(self, event):
        """處理命令"""
        command = self.current_input
        if command:
            self.command_history.append(command)
            self.history_index = len(self.command_history)
            
            # 更新歷史顯示
            self.history_text.config(state=NORMAL)
            self.history_text.insert(tk.END, f"$ {command}\n")
            self.history_text.see(tk.END)
            self.history_text.config(state=DISABLED)
            
            data = self.command_decode(command.lower())
            
            print(data)
            
            # 發送命令
            error = self.command_socket.send_command(data)
            if error:
                self.update_log(error)
            else:
                self.update_log(f"執行指令: {data}")
            
            # 清空輸入
            self.current_input = ""
            self.cursor_position = 0
            self.update_input_display()
    
    def previous_command(self, event):
        """顯示上一個命令"""
        if self.command_history and self.history_index > 0:
            self.history_index -= 1
            self.current_input = self.command_history[self.history_index]
            self.cursor_position = len(self.current_input)
            self.update_input_display()
    
    def next_command(self, event):
        """顯示下一個命令"""
        if self.history_index < len(self.command_history) - 1:
            self.history_index += 1
            self.current_input = self.command_history[self.history_index]
            self.cursor_position = len(self.current_input)
            self.update_input_display()
        
    def update_log(self, message):
        """更新日誌顯示"""
        self.log_text.config(state=NORMAL)
        self.log_text.insert(END, f"{message}\n")
        self.log_text.see(END)
        self.log_text.config(state=DISABLED)
    
    def __del__(self):
        """析構函數，確保程式結束時關閉socket"""
        if hasattr(self, 'command_socket'):
            self.command_socket.close()

def testing():
    time.sleep(3)
    app.input_char('a')  # 輸入字母 'a'
    time.sleep(1)
    app.input_char('1')  # 輸入數字 '1'
    time.sleep(1)
    for _ in range(5):
        app.move_cursor_left()
        time.sleep(0.5)
        app.input_char('B')
        time.sleep(0.5)
    app.backspace()  # 退格
    
    time.sleep(5)
    testing()

def start_api(gui):
    api.main(gui=gui)
    
def main():
    # new thread to process mainloop
    root = ttk.Window(themename="darkly")
    app = TerminalGUI(root)
    thread = threading.Thread(target=start_api, args=(app,), daemon=True)
    thread.start()
    root.mainloop()
    

if __name__ == "__main__":
    main()    
    