import asyncio
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import ccxt.pro as ccxtpro
from datetime import datetime

# 1. مخزن الذاكرة المركزي لحفظ الصفقات المقتنصة لعرضها في المتصفح
captured_opportunities = []
balance_usdt = 1000.0
total_opportunities = 0

# خادم ويب ذكي فائق الخفة متوافق مع سرعة الـ HFT
class SimpleWeb(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        
        html = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>لوحة تحكم البلاك بوكس الخارق</title>
            <style>
                body {{ font-family: Arial, sans-serif; background: #0c0c0c; color: #fff; text-align: center; padding: 20px; }}
                table {{ width: 100%; max-width: 650px; margin: 20px auto; border-collapse: collapse; background: #141414; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }}
                th, td {{ padding: 12px; border: 1px solid #222; text-align: center; }}
                th {{ background: #00e676; color: #000; font-weight: bold; }}
                tr:nth-child(even) {{ background: #1a1a1a; }}
                .no-data {{ color: #666; font-style: italic; }}
                .badge {{ background: #2979ff; padding: 4px 8px; border-radius: 4px; font-size: 12px; }}
            </style>
        </head>
        <body>
            <h2>⚡ رادار المراجحة المثلثية الخارق (HFT V2)</h2>
            <p>حالة المحرك: <span style="color:#00e676; font-weight:bold;">مستقر ويقنص بالملي ثانية 🚀</span></p>
            <p><strong>الرصيد الحالي بالمحاكاة: ${balance_usdt:.2f}</strong></p>
            <table>
                <tr>
                    <th>رقم الصفقة</th>
                    <th>التوقيت</th>
                    <th>المثلث الناجح</th>
                    <th>العائد الصافي</th>
                </tr>
        """
        
        if not captured_opportunities:
            html += "<tr><td colspan='4' class='no-data'>المحرك يمسح 45 قناة سعرية بدقة.. بانتظار الفرصة القادمة..</td></tr>"
        else:
            for opp in reversed(captured_opportunities): # عرض الأحدث أولاً
                html += f"<tr><td>{opp['id']}</td><td>{opp['time']}</td><td><span class='badge'>{opp['mesh']}</span></td><td style='color:#00e676;'>+{opp['return']:.4f}%</td></tr>"
                
        html += """
            </table>
        </body>
        </html>
        """
        self.wfile.write(html.encode('utf-8'))
        
    def log_message(self, format, *args): 
        return

# تشغيل خادم الويب في خلفية النظام
PORT = int(os.environ.get('PORT', 10000))
def start_web_server():
    try:
        server = HTTPServer(('0.0.0.0', PORT), SimpleWeb)
        server.serve_forever()
    except Exception:
        pass

threading.Thread(target=start_web_server, daemon=True).start()

# 2. إعداد محرك الاتصال فائق السرعة بمنصة Gate.io
exchange = ccxtpro.gate({
    'enableRateLimit': True,
    'options': {
        'defaultType': 'spot',
        'ws': {'options': {'concurrency': 50}}
    }
})

FEE_PER_LEG = 0.0006  # 0.06% عمولة VIP
TOTAL_FEE_3_LEGS = FEE_PER_LEG * 3

# القائمة المحدثة للعملات الساخنة
HOT_ALTCOINS = ['SOL', 'XRP', 'DOGE', 'ADA', 'AVAX', 'LINK', 'DOT', 'SHIB', 'NEAR', 'PEPE', 'FET', 'SUI', 'APT', 'WIF', 'BONK']
orderbook_cache = {'BTC/USDT': {'ask': None, 'bid': None}}

for coin in HOT_ALTCOINS:
    orderbook_cache[f'{coin}/USDT'] = {'ask': None, 'bid': None}
    orderbook_cache[f'{coin}/BTC']  = {'ask': None, 'bid': None}

def process_triangular_arbitrage(coin):
    global balance_usdt, total_opportunities
    try:
        pair_usdt = f'{coin}/USDT'
        pair_btc  = f'{coin}/BTC'
        pair_base = 'BTC/USDT'
        
        p_base_ask = orderbook_cache[pair_base]['ask']
        p_coin_btc_bid = orderbook_cache[pair_btc]['bid']
        p_coin_usdt_bid = orderbook_cache[pair_usdt]['bid']
        
        if not (p_base_ask and p_coin_btc_bid and p_coin_usdt_bid):
            return

        raw_return = (1 / p_base_ask) / p_coin_btc_bid * p_coin_usdt_bid
        net_return = raw_return - TOTAL_FEE_3_LEGS
        
        if net_return > 1.0002:
            total_opportunities += 1
            profit_percentage = (net_return - 1) * 100
            gained = balance_usdt * (net_return - 1)
            balance_usdt += gained
            
            current_time = datetime.now().strftime("%H:%M:%S")
            
            # حفظ الصفقة فوراً لعرضها في المتصفح
            captured_opportunities.append({
                'id': total_opportunities,
                'time': current_time,
                'mesh': f"USDT➔BTC➔{coin}",
                'return': profit_percentage,
                'balance': balance_usdt
            })
            
            print(f"\n🚨 [اقتناص خارق || {current_time}] | المثلث: {coin} | الرصيد: ${balance_usdt:.2f}\n", flush=True)
            
    except Exception:
        pass

async def watch_ticker_stream(symbol):
    while True:
        try:
            ticker = await exchange.watch_ticker(symbol)
            if ticker and 'ask' in ticker and 'bid' in ticker:
                orderbook_cache[symbol]['ask'] = ticker['ask']
                orderbook_cache[symbol]['bid'] = ticker['bid']
                
                if symbol == 'BTC/USDT':
                    for coin in HOT_ALTCOINS:
                        process_triangular_arbitrage(coin)
                else:
                    process_triangular_arbitrage(symbol.split('/')[0])
        except Exception:
            await asyncio.sleep(1)

async def main():
    print("⚡ إطلاق محرك البلاك بوكس الخارق المدمج بالويب ⚡")
    tasks = [watch_ticker_stream('BTC/USDT')]
    for coin in HOT_ALTCOINS:
        tasks.append(watch_ticker_stream(f'{coin}/USDT'))
        tasks.append(watch_ticker_stream(f'{coin}/BTC'))
    try:
        await asyncio.gather(*tasks)
    finally:
        await exchange.close()

if __name__ == '__main__':
    asyncio.run(main())
