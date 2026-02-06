from socket_ import SocketSender
import time
ss = SocketSender(10000, "192.168.0.103")

message = ['text', {'content_list': ['You come la, sensei.', 'Still is old sheep son', 'look get up one face tired status ya.'], 'emotion': 'smile'}]

ss.send(message)

time.sleep(2)

change = ['size_final', 2]

ss.send(change)

ss.close()