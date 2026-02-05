from PySide6.QtCore import QThread, Signal
import socket
import time
from json import loads

class SocketListener(QThread):
    def __init__(self, signal: Signal, address='localhost'):
        super().__init__()

        self.signal = signal
        self.address = address
        self.port = 10000
        self.running = True

    def run(self):
        sock = None
        while self.running and self.port <= 10009:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.1)  # 设置超时，避免无限阻塞
                sock.bind((self.address, self.port))
                sock.listen(1)
                print(f"[DEBUG]Listening on {self.address}:{self.port}")

                while self.running:
                    try:
                        conn, addr = sock.accept()  # 这个 accept 也会受 timeout 控制
                        while self.running:
                            data = conn.recv(1024)
                            if not data:
                                break  # 如果没有数据，跳出内层循环
                            message = loads(data.decode())
                            print(f"[DEBUG]Socket Received: {message}")
                            self.signal.emit(*message)
                    except socket.timeout:
                        continue  # 超时，继续检查 self.running
                    except Exception as e:
                        print(f"[ERROR]Socket Accept Error: {e}")
                        break  # 出错跳出内层循环，尝试下一个端口

            except Exception as e:
                print(f"[ERROR]Failed to bind on port {self.address}:{self.port}: {e}")
                sock = None
                self.port += 1
                time.sleep(0.1)  # 稍微等待再试

        if not self.running:
            print("[WARNING]Socket listener stopped by user.")
        else:
            print("[ERROR]All ports from 10000 to 10009 failed.")



# other
class SocketSender:
    def __init__(self, port: int, address='localhost'):
        self.sock = None
        try:
            self.sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((address, port))
        except Exception as e:
            print(f"[ERROR]Socket Connecting Error: {e}")

    def send(self, message: str):
        """
        Format: List[key: str, value: Any]
        """
        from json import dumps
        if self.sock:
            try:
                self.sock.sendall(dumps(message).encode())
            except Exception as e:
                print(f"[ERROR]Socket Sending Error: {e}")
    def close(self):
        if self.sock:
            self.sock.close()
            