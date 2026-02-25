import time
import functools
from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
import socket

class KeepAliveRequestHandler(SimpleXMLRPCRequestHandler):
    # 關鍵：設定協定版本為 HTTP/1.1 以支援 Keep-Alive
    protocol_version = "HTTP/1.1"


class FastXMLRPCServer(SimpleXMLRPCServer):
    def server_bind(self):
        # 1. 先執行原本的綁定邏輯
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # 2. 關鍵：關閉 Nagle's Algorithm，立即發送小封包
        self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        # 3. 完成綁定
        SimpleXMLRPCServer.server_bind(self)


class RPCProfiler:
    def __init__(self):
        # 儲存上一次呼叫「結束」的時間點
        self.last_call_end = None

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            now = time.perf_counter()

            # 計算距離上一次 RPC 呼叫結束的時間差 (以微秒 us 為單位)
            if self.last_call_end is None:
                interval_us = "First Call"
            else:
                # 1 秒 = 1,000,000 微秒
                interval_us = f"{(now - self.last_call_end) * 1_000_000:.2f} us"

            # 執行函式並計算本次耗時 (Elapsed)
            start_exec = time.perf_counter()
            result = func(*args, **kwargs)
            end_exec = time.perf_counter()

            elapsed_us = (end_exec - start_exec) * 1_000_000

            # 更新結束時間供下次呼叫參考
            self.last_call_end = end_exec

            # 印出分析結果
            #print(f"[{func.__name__}]")
            print(f"  > 本次執行耗時 (Elapsed): {elapsed_us:.2f} us")
            print(f"  > 距離前次呼叫 (Interval): {interval_us}")
            #print("-" * 30)

            return result
        return wrapper

# 實例化 Profiler
profiler = RPCProfiler()

# 設定伺服器
server = FastXMLRPCServer(("localhost", 50002), logRequests=False, requestHandler=KeepAliveRequestHandler)

@profiler
def add(x, y):
    # 模擬簡單運算
    return x + y

@profiler
def is_even(n):
    # 模擬簡單邏輯
    return n % 2 == 0

@profiler
def process_payload(raw_string):
    """
    假設傳入格式為 "address:127.0.0.1;message:Hello Server"
    """
    try:
        # 1. 拆分字串
        parts = raw_string.split(";")
        data_dict = {}
        
        for part in parts:
            key, value = part.split(":")
            data_dict[key] = value
            
        # 2. 提取具體欄位
        addr = data_dict.get("address", "未知地址")
        content = data_dict.get("message", "無內容")
        
        #print(f"--- 拆解成功 ---")
        #print(f"來源地址: {addr}")
        #print(f"內容數據: {content}")
        
        return {"status": "success", "received_address": addr}
    
    except Exception as e:
        return {"status": "error", "reason": str(e)}


server.register_function(add, "add")
server.register_function(is_even, "is_even")
server.register_function(process_payload, "unpack_data")

print("Server is running on port 50002 (Timing in microseconds)...")
server.serve_forever()
