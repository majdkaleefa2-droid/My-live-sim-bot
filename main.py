
import time
import ccxt
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# 1. إعداد السيرفر الوهمي بأبسط طريقة ممكنة لمنع تعارض ريندر
class SimpleWeb(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Bot Active")
    def log_message(self, format, *args):
        return  # كتم سجلات السيرفر الوهمي لمنع زحمة الشاشة

def start_server():
    try:
        server = HTTPServer(('0.0.0.0', 10000), SimpleWeb)
        server.serve_forever()
    except Exception:
        pass

# تشغيل السيرفر في مسار خلفي مستقل تماماً قبل أي شيء
threading.Thread(target=start_server, daemon=True).start()
time.sleep(1)

print("📐 تشغيل محاكي المراجحة المثلثية الحي (Triangular Arbitrage)...", flush=True)
print("-" * 75, flush=True)

# 2. بدء الاتصال الفوري ببينانس
exchange = ccxt.binance()
demo_balance = 1000.0  
fee_rate = 0.00075     # عمولة المزاد التراكمية المخفضة (0.075%)
total_opportunities = 0
successful_trades = 0

print(f"💰 الرصيد الابتدائي المحفوظ في السيرفر: ${demo_balance:.2f}", flush=True)
print("-" * 75, flush=True)

# 3. فحص الدورة المثلثية اللحظية وبثها فوراً للشاشة
while True:
    try:
        btc_ticker = exchange.fetch_ticker('BTC/USDT')
        eth_ticker = exchange.fetch_ticker('ETH/USDT')
        eth_btc_ticker = exchange.fetch_ticker('ETH/BTC')
        
        p_btc_usdt = btc_ticker['ask']        
        p_eth_btc = eth_btc_ticker['bid']     
        p_eth_usdt = eth_ticker['bid']        
        
        raw_return = (1 / p_btc_usdt) / p_eth_btc * p_eth_usdt
        total_fees = fee_rate * 3
        net_return_rate = raw_return - total_fees
        
        # طباعة نبض السوق بشكل فوري وحي دون أي تجميد
        print(f"🔄 فحص حي | BTC: ${p_btc_usdt:.1f} | العائد الصافي للدورة: {net_return_rate:.5f}", flush=True)
        
        if net_return_rate > 1.0001:
            total_opportunities += 1
            successful_trades += 1
            
            trade_amount = demo_balance * 0.50
            profit = trade_amount * (net_return_rate - 1)
            demo_balance += profit
            
            print(f"\n🚨 [اقتناص فرصة ربح حقيقية!] | صفقة رقم: {successful_trades} | الرصيد الحالي: ${demo_balance:.2f}\n", flush=True)
            
    except Exception as e:
        pass
        
    time.sleep(3)
