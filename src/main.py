import USB.receive
import GUI.main
import threading

if __name__ == "__main__":
    # 啟動USB接收端
    usb_thread = threading.Thread(target=USB.receive.main, daemon=True)
    usb_thread.start()
    
    GUI.main.main()