import time
import ccxt
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# هذا هو الجزء السحري لفتح منفذ وهمي يخدع السيرفر المجاني ويمنعه من الوقوف
class WebServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Bot is Running Safely!")

def run_web_server():
    # المنفذ 10000 هو المطلوب تماماً لمنصة ريندر مجاناً
    server = HTTPServer(('0.0.0.0', 10000), WebServer)
    server.serve_forever()

# تشغيل السيرفر الوهمي في الخلفية كمسار مستقل
threading.Thread(target=run_web_server, daemon=True).start()

print("⚡ بَدْء تشغيل البوت المجاني بمحفظة وهمية وسعر حي من بينانس...")
print("-" * 60)

exchange = ccxt.binance()
USDT_BALANCE = 1000.0  
TOTAL_FEES = 0.001 * 3 

while True:
    try:
        btc_ask = exchange.fetch_ticker('BTC/USDT')['ask']
        eth_btc_bid = exchange.fetch_ticker('ETH/BTC')['bid']
        eth_bid = exchange.fetch_ticker('ETH/USDT')['bid']
        
        raw_return = (1 / btc_ask) / (1 / eth_btc_bid) * eth_bid
        net_return = raw_return * (1 - TOTAL_FEES)
        
        print(f"🔄 فحص مجاني | BTC: {btc_ask:.1f} | العائد الصافي: {net_return:.5f}")
        
        if net_return > 1.0001: 
            profit_percent = (net_return - 1) * 100
            old_balance = USDT_BALANCE
            USDT_BALANCE = USDT_BALANCE * net_return
            print(f"🚨 [اقتناص فرصة ربح حقيقية in السوق!]")
            print(f"📈 النسبة: +{profit_percent:.4f}% | الرصيد: {USDT_BALANCE:.2f} USDT")
            print("-" * 40)
            
    except Exception as e:
        pass
        
    time.sleep(3)
