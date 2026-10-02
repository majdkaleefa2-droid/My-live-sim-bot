import asyncio
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import ccxt.pro as ccxtpro

# 1. خادم ويب متوافق تماماً مع ريندر و Cron-Job
class SimpleWeb(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"OK")  # رد بسيط وسريع جداً لإغلاق الطلب فوراً
    def log_message(self, format, *args): 
        return

PORT = int(os.environ.get('PORT', 10000))

def start_web_server():
    server = HTTPServer(('0.0.0.0', PORT), SimpleWeb)
    server.serve_forever()

threading.Thread(target=start_web_server, daemon=True).start()

# 2. إعداد الحساب
exchange = ccxtpro.gate({'enableRateLimit': True}) 
demo_balance = 1000.0  
fee_rate = 0.002  
total_opportunities = 0

shared_ticker_data = {
    'BTC/USDT': None,
    'ETH/USDT': None,
    'ETH/BTC': None
}

# 3. دالة الفحص المستقرة (تعديل الأمان والسرعة)
async def analyze_arbitrage():
    global demo_balance, total_opportunities
    
    while True:
        try:
            if not all(shared_ticker_data.values()):
                # تم زيادة وقت الانتظار الأولي لضمان استقرار قنوات البث
                await asyncio.sleep(1)
                continue
            
            p_btc_usdt = shared_ticker_data['BTC/USDT']['ask']
            p_eth_btc = shared_ticker_data['ETH/BTC']['bid']
            p_eth_usdt = shared_ticker_data['ETH/USDT']['bid']
            
            if not p_btc_usdt or not p_eth_btc or not p_eth_usdt:
                continue
                
            raw_return = (1 / p_btc_usdt) / p_eth_btc * p_eth_usdt
            net_return_rate = raw_return - (fee_rate * 3)
            
            print(f"⚡ [Gate.io بث حي] العائد: {net_return_rate:.5f} | BTC: ${p_btc_usdt:.1f}", flush=True)
            
            if net_return_rate > 1.0001:
                total_opportunities += 1
                trade_amount = demo_balance * 0.50
                profit = trade_amount * (net_return_rate - 1)
                demo_balance += profit
                print(f"\n🚨 [اقتناص فرصة] | صفقة: {total_opportunities} | الرصيد: ${demo_balance:.2f}\n", flush=True)
                
        except Exception as e:
            print(f"⚠️ خطأ في التحليل: {e}", flush=True)
            
        # تـــم الـتـعـديل هـنـا: رفع وقت الانتظار إلى (1 ثانية) بدلاً من (10 ملي ثانية) 
        # هذا يمنع السيرفر المجاني من حظر الكود بسبب الضغط العالي ويضمن استمراره للأبد
        await asyncio.sleep(1)

# 4. دالة الاستماع المستمر للبث
async def watch_pair(symbol):
    print(f"📡 فتح قناة WebSocket للزوج: {symbol}", flush=True)
    while True:
        try:
            ticker = await exchange.watch_ticker(symbol)
            shared_ticker_data[symbol] = ticker
        except Exception as e:
            print(f"🚨 خطأ في قناة {symbol}: {e}", flush=True)
            # انتظار أطول عند حدوث خطأ شبكة لإعادة الاتصال الآمن
            await asyncio.sleep(5)

async def main():
    try:
        await asyncio.gather(
            watch_pair('BTC/USDT'),
            watch_pair('ETH/USDT'),
            watch_pair('ETH/BTC'),
            analyze_arbitrage()
        )
    except Exception as main_err:
        print(f"❌ خطأ في المحرك الرئيسي: {main_err}", flush=True)
    finally:
        await exchange.close()

if __name__ == '__main__':
    asyncio.run(main())
