import asyncio
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import ccxt.pro as ccxtpro
import json
from datetime import datetime

# مخزن ذاكرة مركزي لحفظ الفرص المقتنصة فقط لمراجعتها لاحقاً
captured_opportunities = []

# 1. خادم ويب ذكي يعرض تقرير الفرص المقتنصة مباشرة في المتصفح
class SimpleWeb(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        
        # بناء صفحة ويب بسيطة ومريحة للمراجعة من الهاتف
        html = """
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>تقرير المراجحة المثلثية</title>
            <style>
                body { font-family: Arial, sans-serif; background: #121212; color: #fff; text-align: center; padding: 20px; }
                table { width: 100%; max-width: 600px; margin: 20px auto; border-collapse: collapse; background: #1e1e1e; }
                th, td { padding: 12px; border: 1px solid #333; text-align: center; }
                th { background: #ff9800; color: #000; }
                .no-data { color: #888; font-style: italic; }
            </style>
        </head>
        <body>
            <h2>📊 رادار المراجحة المثلثية الحي - تقرير الفرص</h2>
            <p>حالة البوت: <span style="color:#4caf50; font-weight:bold;">نشط ويعمل ⚡</span></p>
            <table>
                <tr>
                    <th>رقم الصفقة</th>
                    <th>التوقيت</th>
                    <th>العائد الصافي</th>
                    <th>الرصيد الحالي</th>
                </tr>
        """
        
        if not captured_opportunities:
            html += "<tr><td colspan='4' class='no-data'>لم يتم اقتناص أي فرصة بعد، الرادار يبحث بالثانية...</td></tr>"
        else:
            for opp in captured_opportunities:
                html += f"<tr><td>{opp['id']}</td><td>{opp['time']}</td><td>{opp['return']:.5f}</td><td>${opp['balance']:.2f}</td></tr>"
                
        html += """
            </table>
        </body>
        </html>
        """
        self.wfile.write(html.encode('utf-8'))
        
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

# 3. دالة الفحص المستقرة والاقتناص اللحظي
async def analyze_arbitrage():
    global demo_balance, total_opportunities
    
    while True:
        try:
            if not all(shared_ticker_data.values()):
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
                
                # حفظ الفرصة فوراً في جدول الذاكرة للمراجعة لاحقاً
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                captured_opportunities.append({
                    'id': total_opportunities,
                    'time': current_time,
                    'return': net_return_rate,
                    'balance': demo_balance
                })
                
                print(f"\n🚨 [اقتناص فرصة] | صفقة: {total_opportunities} | الرصيد: ${demo_balance:.2f}\n", flush=True)
                
        except Exception as e:
            print(f"⚠️ خطأ في التحليل: {e}", flush=True)
            
        await asyncio.sleep(1)

# 4. دالة استيعاب البث
async def watch_pair(symbol):
    print(f"📡 فتح قناة WebSocket للزوج: {symbol}", flush=True)
    while True:
        try:
            ticker = await exchange.watch_ticker(symbol)
            shared_ticker_data[symbol] = ticker
        except Exception as e:
            print(f"🚨 خطأ في قناة {symbol}: {e}", flush=True)
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
