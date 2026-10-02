import asyncio
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import ccxt.pro as ccxtpro  # المكتبة الاحترافية للبث الحي عبر WebSocket

# 1. خادم الويب الأساسي لإبقاء منصة ريندر مستيقظة
class SimpleWeb(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"HFT Arbitrage Bot is active and streaming via WebSockets!")
    def log_message(self, format, *args): 
        return

PORT = int(os.environ.get('PORT', 10000))

def start_web_server():
    server = HTTPServer(('0.0.0.0', PORT), SimpleWeb)
    server.serve_forever()

# تشغيل خادم الويب في خيط مستقل لمنع تعارض سرعة البوت
threading.Thread(target=start_web_server, daemon=True).start()

# 2. إعداد الحساب والمحاكاة الافتراضية
# قمنا بتغيير المنصة إلى Bybit وتفعيل بروتوكول الـ Pro (WebSockets)
exchange = ccxtpro.bybit({'enableRateLimit': False}) 

demo_balance = 1000.0  
fee_rate = 0.0006  # رسوم الميكر/تيكر العادية في Bybit (غالباً أقل من بينانس)
total_opportunities = 0

# مخزن مؤقت لحفظ الأسعار في الذاكرة لسرعة ميكرو ثانية
shared_ticker_data = {
    'BTC/USDT': None,
    'ETH/USDT': None,
    'ETH/BTC': None
}

# 3. دالة معالجة وفحص المراجحة المثلثية بسرعة البرق
async def analyze_arbitrage():
    global demo_balance, total_opportunities
    
    while True:
        try:
            # التأكد من أن جميع الأزواج استقبلت أسعارها الأولى
            if not all(shared_ticker_data.values()):
                await asyncio.sleep(0.01)
                continue
            
            p_btc_usdt = shared_ticker_data['BTC/USDT']['ask']
            p_eth_btc = shared_ticker_data['ETH/BTC']['bid']
            p_eth_usdt = shared_ticker_data['ETH/USDT']['bid']
            
            if not p_btc_usdt or not p_eth_btc or not p_eth_usdt:
                continue
                
            # معادلة المراجحة المثلثية في الذاكرة (RAM)
            raw_return = (1 / p_btc_usdt) / p_eth_btc * p_eth_usdt
            net_return_rate = raw_return - (fee_rate * 3)
            
            # طباعة الفحص بسرعة البرق في السجلات
            print(f"⚡ [بث حي] العائد الصافي: {net_return_rate:.5f} | BTC: ${p_btc_usdt:.1f}", flush=True)
            
            if net_return_rate > 1.0001:
                total_opportunities += 1
                trade_amount = demo_balance * 0.50
                profit = trade_amount * (net_return_rate - 1)
                demo_balance += profit
                
                print(f"\n🚨 [اقتناص فرصة بلمح البصر!] | صفقة: {total_opportunities} | الرصيد: ${demo_balance:.2f}\n", flush=True)
                
        except Exception as e:
            print(f"⚠️ خطأ أثناء التحليل اللحظي: {e}", flush=True)
            
        # فحص مستمر بفارق ضئيل جداً لإراحة المعالج (10 ملي ثانية)
        await asyncio.sleep(0.01)

# 4. دالة استيعاب وتلقي البث الحي لكل زوج عملات بشكل منفصل ومستمر
async def watch_pair(symbol):
    print(f"📡 بدء فتح قناة WebSocket للزوج: {symbol}", flush=True)
    while True:
        try:
            # دالة watch_ticker تستمع للبث الحي القادم من Bybit فوراً
            ticker = await exchange.watch_ticker(symbol)
            shared_ticker_data[symbol] = ticker
        except Exception as e:
            print(f"🚨 خطأ في قناة WebSocket للزوج {symbol}: {e}", flush=True)
            await asyncio.sleep(1)

# 5. تشغيل المهام غير المتزامنة بالتوازي
async def main():
    symbols = ['BTC/USDT', 'ETH/USDT', 'ETH/BTC']
    
    # تشغيل قنوات الاستماع للأزواج الثلاثة مع دالة التحليل في نفس الوقت
    await asyncio.gather(
        watch_pair(symbols[0]),
        watch_pair(symbols[1]),
        watch_pair(symbols[2]),
        analyze_arbitrage()
    )

if __name__ == '__main__':
    # تشغيل حلقة محرك asyncio الاحترافية
    asyncio.run(main())
