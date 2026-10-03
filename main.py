import asyncio
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import ccxt.pro as ccxtpro
from datetime import datetime

# الذاكرة المركزية ورصيد المحاكاة الصارم
captured_opportunities = []
balance_usdt = 1000.0
total_opportunities = 0

# ==========================================
# 🛑 طبقة حماية المخاطر وضوابط الأمان الصارمة (Risk Settings)
# ==========================================
MAX_TRADE_SIZE_USDT = 50.0  # حد حجم الصفقة الواحدة (حماية من الانزلاق السعري)
MIN_ORDER_BOOK_DEPTH = 150.0  # يجب توفر سيولة بقيمة 150$ على الأقل عند السعر المعروض لتنفيذ الصفقة
MAX_CONSECUTIVE_FAILURES = 2  # حد الفشل المتتالي لتفعيل مفتاح القطع
consecutive_failures = 0
kill_switch_activated = False
# ==========================================

class SimpleWeb(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        
        status_text = "نشط ويقنص بأمان حقيقي 🛡️" if not kill_switch_activated else "🚨 مُغلق تلقائياً (Kill Switch) لحماية الحساب!"
        status_color = "#00e676" if not kill_switch_activated else "#ff1744"
        
        html = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>البلاك بوكس المحترف - إدارة المخاطر</title>
            <style>
                body {{ font-family: Arial, sans-serif; background: #0a0a0c; color: #fff; text-align: center; padding: 20px; }}
                table {{ width: 100%; max-width: 650px; margin: 20px auto; border-collapse: collapse; background: #111116; box-shadow: 0 4px 15px rgba(0,0,0,0.7); }}
                th, td {{ padding: 12px; border: 1px solid #222530; text-align: center; }}
                th {{ background: #2979ff; color: #fff; font-weight: bold; }}
                tr:nth-child(even) {{ background: #171721; }}
                .no-data {{ color: #555; font-style: italic; }}
                .badge {{ background: #00e676; color: #000; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight:bold; }}
            </style>
        </head>
        <body>
            <h2>🛡️ محرك المراجحة المحترف - إدارة المخاطر العالية (V3)</h2>
            <p>حالة المحرك: <span style="color:{status_color}; font-weight:bold;">{status_text}</span></p>
            <p><strong>الرصيد المحمي بالمحاكاة: ${balance_usdt:.2f}</strong> | حجم الصفقة الأقصى: ${MAX_TRADE_SIZE_USDT}</p>
            <table>
                <tr>
                    <th>رقم الصفقة</th>
                    <th>التوقيت</th>
                    <th>المثلث</th>
                    <th>العائد الصافي</th>
                </tr>
        """
        if not captured_opportunities:
            html += "<tr><td colspan='4' class='no-data'>المحرك يمسح قنوات السيولة بعمق.. بانتظار فرصة تطابق شروط الأمان الصارمة..</td></tr>"
        else:
            for opp in reversed(captured_opportunities):
                html += f"<tr><td>{opp['id']}</td><td>{opp['time']}</td><td><span class='badge'>{opp['mesh']}</span></td><td style='color:#00e676;'>+{opp['return']:.4f}%</td></tr>"
        html += "</table></body></html>"
        self.wfile.write(html.encode('utf-8'))
        
    def log_message(self, format, *args): return

PORT = int(os.environ.get('PORT', 10000))
def start_web_server():
    try:
        server = HTTPServer(('0.0.0.0', PORT), SimpleWeb)
        server.serve_forever()
    except Exception: pass

threading.Thread(target=start_web_server, daemon=True).start()

exchange = ccxtpro.gate({
    'enableRateLimit': True,
    'options': {'defaultType': 'spot', 'ws': {'options': {'concurrency': 50}}}
})

FEE_PER_LEG = 0.0006  
TOTAL_FEE_3_LEGS = FEE_PER_LEG * 3

HOT_ALTCOINS = ['SOL', 'XRP', 'DOGE', 'ADA', 'AVAX', 'LINK', 'DOT', 'SHIB', 'NEAR', 'PEPE', 'FET', 'SUI', 'APT', 'WIF', 'BONK']
orderbook_cache = {}

async def watch_order_book_stream(symbol):
    """
    تحديث البث الحي لعمق دفتر الطلبات (Order Book Depth) مجاناً 
    بدلاً من الـ Ticker العادي، لضمان قراءة السيولة المتوفرة
    """
    global kill_switch_activated
    while True:
        if kill_switch_activated:
            await asyncio.sleep(5)
            continue
        try:
            # سحب عمق طلبات حقيقي (أفضل 5 طلبات شراء وبيع)
            orderbook = await exchange.watch_order_book(symbol, limit=5)
            if orderbook and orderbook['asks'] and orderbook['bids']:
                # حفظ السعر والكمية المتوفرة عند هذا السعر (السعر، الكمية)
                orderbook_cache[symbol] = {
                    'ask_price': orderbook['asks'][0][0],
                    'ask_volume': orderbook['asks'][0][1] * orderbook['asks'][0][0], # القيمة بالدولار
                    'bid_price': orderbook['bids'][0][0],
                    'bid_volume': orderbook['bids'][0][1] * orderbook['bids'][0][0]  # القيمة بالدولار
                }
                
                # إطلاق الفحص
                if symbol == 'BTC/USDT':
                    for coin in HOT_ALTCOINS: process_safe_arbitrage(coin)
                else:
                    process_safe_arbitrage(symbol.split('/')[0])
        except Exception:
            await asyncio.sleep(1)

def process_safe_arbitrage(coin):
    global balance_usdt, total_opportunities, kill_switch_activated, consecutive_failures
    
    if kill_switch_activated: return
    
    try:
        pair_usdt = f'{coin}/USDT'
        pair_btc  = f'{coin}/BTC'
        pair_base = 'BTC/USDT'
        
        if not (pair_base in orderbook_cache and pair_btc in orderbook_cache and pair_usdt in orderbook_cache):
            return
            
        # 1. جلب الأسعار والسيولة المتوفرة لكل طرف في المثلث
        base = orderbook_cache[pair_base]
        leg2 = orderbook_cache[pair_btc]
        leg3 = orderbook_cache[pair_usdt]
        
        # 2. تطبيق فلتر السيولة الصارم (Liquidity Gate)
        # التأكد من أن قيمة الطلبات المعروضة عند هذه الأسعار أكبر من الحد الأدنى المطلوب لصفقتنا
        if (base['ask_volume'] < MIN_ORDER_BOOK_DEPTH or 
            (leg2['bid_volume'] * base['ask_price']) < MIN_ORDER_BOOK_DEPTH or 
            leg3['bid_volume'] < MIN_ORDER_BOOK_DEPTH):
            return # تخطي الفرصة فوراً لو السيولة ضعيفة لتجنب خسارة الانزلاق السعري
            
        p_base_ask = base['ask_price']
        p_coin_btc_bid = leg2['bid_price']
        p_coin_usdt_bid = leg3['bid_price']
        
        raw_return = (1 / p_base_ask) / p_coin_btc_bid * p_coin_usdt_bid
        net_return = raw_return - TOTAL_FEE_3_LEGS
        
        # عتبة الاقتناص الآمن للسيولة الحقيقية
        if net_return > 1.0003:
            total_opportunities += 1
            profit_percentage = (net_return - 1) * 100
            
            # احتساب الربح بناءً على حجم الصفقة المحدد كأمان وليس كامل المحفظة
            gained = MAX_TRADE_SIZE_USDT * (net_return - 1)
            balance_usdt += gained
            consecutive_failures = 0 # تصفير عداد الفشل عند النجاح
            
            current_time = datetime.now().strftime("%H:%M:%S")
            captured_opportunities.append({
                'id': total_opportunities,
                'time': current_time,
                'mesh': f"USDT➔{coin}",
                'return': profit_percentage,
                'balance': balance_usdt
            })
            
            print(f"🛡️ [صفقة آمنة معتمدة] | العملة: {coin} | الرصيد: ${balance_usdt:.2f}", flush=True)
            
    except Exception:
        consecutive_failures += 1
        if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
            kill_switch_activated = True
            print("🚨 تفعيل مفتاح القطع (Kill Switch)! تم إيقاف البوت لحماية رأس المال.")

async def main():
    print("🚀 إطلاق نسخة البلاك بوكس المحترفة V3 - نظام إدارة المخاطر الحقيقي")
    tasks = [watch_order_book_stream('BTC/USDT')]
    for coin in HOT_ALTCOINS:
        orderbook_cache[f'{coin}/USDT'] = {}
        orderbook_cache[f'{coin}/BTC'] = {}
        tasks.append(watch_order_book_stream(f'{coin}/USDT'))
        tasks.append(watch_order_book_stream(f'{coin}/BTC'))
    try:
        await asyncio.gather(*tasks)
    finally:
        await exchange.close()

if __name__ == '__main__':
    asyncio.run(main())
