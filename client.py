import xmlrpc.client
import http.client
import socket

class KeepAliveTransport(xmlrpc.client.Transport):
    def __init__(self):
        super().__init__()
        self._connection = None

    def make_connection(self, host):
        # 如果連線已存在則重用，否則建立新連線
        if self._connection is None:
            self._connection = http.client.HTTPConnection(host)
            # 建立連線後設定 TCP_NODELAY
            self._connection.connect()
            self._connection.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        return self._connection

# 建立與伺服器的連線代理
with xmlrpc.client.ServerProxy("http://localhost:50002/") as proxy:
    # 呼叫遠端伺服器上的 add 函式
    for _ in range(1000000):
        payload = "address:10.0.0.50;message:這是加密數據"
        response = proxy.unpack_data(payload)
        #result_add = proxy.add(5, 3)
        #print(f"5 + 3 = {result_add}")

        # 呼叫遠端伺服器上的 is_even 函式
        #result_even = proxy.is_even(10)
        #print(f"10 是偶數嗎？ {result_even}")
