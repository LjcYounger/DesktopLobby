from PySide6.QtCore import QThread, Signal
import socket
import time

class SocketListener(QThread):
    def __init__(self, comm):
        super().__init__()
        self.comm = comm
        self.address = 10000
        self.running = True

    def run(self):
        sock = None
        while self.running and self.address <= 10009:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.1)  # 设置超时，避免无限阻塞
                sock.bind(('localhost', self.address))
                sock.listen(1)
                print(f"[DEBUG]Listening on port {self.address}")

                while self.running:
                    try:
                        conn, addr = sock.accept()  # 这个 accept 也会受 timeout 控制
                        data = conn.recv(1024)
                        if data:
                            message = data.decode().strip()
                            self.comm.data_signal.emit(message)
                        conn.close()
                    except socket.timeout:
                        continue  # 超时，继续检查 self.running
                    except Exception as e:
                        print("[ERROR]Socket Accept Error: {e}")
                        break  # 出错跳出内层循环，尝试下一个端口

            except Exception as e:
                print(f"[ERROR]Failed to bind on port {self.address}: {e}")
                sock = None
                self.address += 1
                time.sleep(0.1)  # 稍微等待再试

        if not self.running:
            print("[WARNING]Socket listener stopped by user.")
        else:
            print("[ERROR]All ports from 10000 to 10009 failed.")



# other
class SocketSender:
    def __init__(self, port, address='localhost'):
        self.sock = None
        try:
            self.sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect(('localhost', address))
        except Exception as e:
            print(e)

    def send(self, message):
        if self.sock:
            try:
                self.sock.sendall(message)
            except Exception as e:
                print(e)
    def close(self):
        if self.sock:
            self.sock.close()
            