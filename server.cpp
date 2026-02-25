#include "XmlRpc.h"
#include <iostream>
#include <string>
#include <winsock2.h>
#include <chrono>
#include <iomanip>

#pragma comment(lib, "ws2_32.lib")

using namespace XmlRpc;

static std::chrono::steady_clock::time_point g_lastRpcEnd;



// 1. 定義方法
class UnpackData : public XmlRpcServerMethod {
public:
    UnpackData(XmlRpcServer* s) : XmlRpcServerMethod("unpack_data", s) {}

    void execute(XmlRpcValue& params, XmlRpcValue& result) {
        
auto now = std::chrono::steady_clock::now();

if (g_lastRpcEnd.time_since_epoch().count() != 0)
    {
        auto prev_us = std::chrono::duration_cast<std::chrono::microseconds>
                       (now - g_lastRpcEnd).count();

        std::cout << "prev RPC .. " 
                  << std::right << std::setw(8) << prev_us << " us\n";
    }
    else
    {
        std::cout << "prev RPC .. " << std::setw(8) << "-" << " μs (first call)\n";
    }
    g_lastRpcEnd = now;  // update for next call

        // 直接取得字串，避免過多拷貝
        const std::string& payload = params[0];
       // printf("xxx\n");
        // 快速回傳結果陣列
        result.setSize(1);
        result[0] = "OK";
    }
};

int main() {
    // 效能優化 1：關閉所有 Log 輸出，避免 I/O 阻塞
    setVerbosity(0);

    XmlRpcServer s;
    UnpackData unpack(&s);

    int port = 50002;
    if (!s.bindAndListen(port)) {
        std::cerr << "Error binding to port " << port << std::endl;
        return -1;
    }

    std::cout << "XmlRpc++ Server (Optimized) running on " << port << "..." << std::endl;

    // 效能優化 2：手動獲取底層 Socket 並設定 TCP_NODELAY (視庫實作可能需要微調)
    // XmlRpc++ 通常在 accept 後會處理，若要強制全域，可在此設定

    // 進入無窮迴圈處理請求
    // work(-1.0) 會阻塞並持續處理 Keep-Alive 連線
    s.work(-1.0);

    return 0;
}