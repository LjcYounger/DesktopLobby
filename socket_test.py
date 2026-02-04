from socket_ import SocketSender
import time
ss = SocketSender(10001)

message = ['text', {'content_list': ['You come la, sensei.', 'Still is old sheep son', 'look get up one face tired status ya.'], 'emotion': 'smile'}]

ss.send(message)

time.sleep(2)

ss.send(message)

ss.close()