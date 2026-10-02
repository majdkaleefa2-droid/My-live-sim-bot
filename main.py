
import time
import ccxt
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import os  # تم استيراده لقراءة منفذ ريندر تلقائياً

# 1. خادم الويب الأساسي لإرضاء منصة ريندر وتجنب توقف السيرفر
class SimpleWeb(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Bot is active and logging!")
    def log_message(self, format, *args): 
        return

# جلب المنفذ من ريندر تلقائياً، وإذا لم يجده يستخدم 10000 كافتراضي
PORT = int(os.environ.get('PORT', 10000))

def run_server():
    server = HTTPServer(('0.0.0.0', PORT), SimpleWeb)
    print(f"🌍 Web server running on port {PORT}")
    server.serve_forever()

# تشغيل خادم الويب في خلفية الكود
threading.Thread(target=run_server, daemon=True).start()

# 2. إعداد الاتصال ببينانس والمحفظة
exchange = ccxt.binance()
demo_balance = 1000.0  
fee_rate = 0.00075     
total_opportunities = 0

# كتابة السطر الترحيبي الأول في ملف السجل
with open("log.txt", "w", encoding="utf-8") as f:
    f.write("📐 تم بدء تشغيل محاكي المراجحة المثلثية الحي...\n")
    f.write(f"💰 الرصيد الابتدائي المحفوظ: ${demo_balance:.2f}\n")
    f.write("-" * 60 + "\n")

# 3. فحص السوق وحفظ البيانات فوراً في ملف log.txt
while True:
    try:
        btc = exchange.fetch_ticker('BTC/USDT')
        eth = exchange.fetch_ticker('ETH/USDT')
        eth_btc = exchange.fetch_ticker('ETH/BTC')
        
        p_btc_usdt = btc['ask']        
        p_eth_btc = eth_btc['bid']     
        
        # تــــم الـتـصـحـيـح هـنـا: استخدام المتغير الصحيح eth بدلاً من eth_ticker
        p_eth_usdt = eth['bid']
        
        raw_return = (1 / p_btc_usdt) / p_eth_btc * p_eth_usdt
        net_return_rate = raw_return - (fee_rate * 3)
        
        # حفظ الفحص الحالي في المستند النصي ول LOG المنصة لترى الحركة
        log_line = f"🔄 فحص حي | BTC: ${p_btc_usdt:.1f} | العائد الصافي: {net_return_rate:.5f}\n"
        print(log_line.strip()) # يطبع في الـ Application logs على ريندر مباشرة
        
        with open("log.txt", "a", encoding="utf-8") as f:
            f.write(log_line)
            
        if net_return_rate > 1.0001:
            total_opportunities += 1
            trade_amount = demo_balance * 0.50
            profit = trade_amount * (net_return_rate - 1)
            demo_balance += profit
            
            profit_line = f"\n🚨 [اقتناص فرصة ربح!] | صفقة رقم: {total_opportunities} | الرصيد الحالي: ${demo_balance:.2f}\n\n"
            print(profit_line.strip())
            with open("log.txt", "a", encoding="utf-8") as f:
                f.write(profit_line)
                
    except Exception as e:
        # طباعة الخطأ في سجلات ريندر بدلاً من تجاوزه بصمت لتعرف إن واجهتك مشكلة اتصال بالإنترنت
        print(f"⚠️ خطأ أثناء الفحص: {e}")
        
    time.sleep(3)
