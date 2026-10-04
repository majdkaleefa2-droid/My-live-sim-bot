import os
import asyncio
import threading
import math
from flask import Flask
from binance import AsyncClient, BinanceSocketManager

app = Flask(__name__)

# لوحة القيادة المالية المؤسساتية المحدثة بنظام العمولات المخفضة BNB
bot_stats = {
    "status": "⚙️ Booting HFT BNB-Optimized V5...",
    "balance_usdt": 10000.0,
    "net_profit_usdt": 0.0,
    "total_trades": 0,
    "last_alert": "Engine tracking 15 assets with 25% BNB fee discount..."
}

@app.route('/')
def home():
    html = f"""
    <html>
        <head>
            <meta http-equiv="refresh" content="1">
            <title>HFT V5 - BNB Fees Simulated</title>
            <style>
                body {{ font-family: 'Courier New', monospace; background: #030303; color: #00ff00; padding: 20px; text-align: center; }}
                .dashboard {{ border: 2px solid #ffcc00; padding: 25px; display: inline-block; background: #111; border-radius: 8px; text-align: left; min-width: 530px; box-shadow: 0 0 25px rgba(255,204,0,0.3); }}
                h2 {{ color: #ffcc00; text-align: center; margin-top: 0; }}
                .metric {{ color: #00ffff; font-weight: bold; }}
                .status {{ color: #5cb85c; font-weight: bold; }}
                .profit {{ color: #5cb85c; font-weight: bold; }}
                .danger {{ color: #d9534f; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="dashboard">
                <h2>⚡ رادار HFT المطور (خصم BNB) - V5</h2>
                <p><b>حالة رادار السيولة:</b> <span class="status">{bot_stats['status']}</span></p>
                <div style="font-size:11px; color:#ffcc00; margin-bottom:10px;">🛡️ درع عمولات BNB المحاكي: نشط (خصم 25%) 🟢</div>
                <hr style="border-color: #222;">
                <p>💵 رأس المال التجريبي: <span class="metric">{bot_stats['balance_usdt']:.2f} USDT</span></p>
                <p>📈 صافي الأرباح الصافية الحقيقية: <span class="{'profit' if bot_stats['net_profit_usdt'] >= 0 else 'danger'}">{bot_stats['net_profit_usdt']:.4f} USDT</span></p>
                <p>🔄 عمليات القنص الإيجابية المنفذة: <span class="metric">{bot_stats['total_trades']} صفقة</span></p>
                <hr style="border-color: #222;">
                <p>🚨 <b>آخر قنص إحصائي فلتره درع الأمان:</b> <br><span style="color: #00ffff; font-size: 12px;">{bot_stats['last_alert']}</span></p>
            </div>
        </body>
    </html>
    """
    return html

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, use_reloader=False)

API_KEY = os.getenv('BINANCE_API_KEY')
SECRET_KEY = os.getenv('BINANCE_SECRET_KEY')

# الـ 15 عملة الحارة تحت الرادار
SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT",
    "DOGEUSDT", "AVAXUSDT", "LINKUSDT", "DOTUSDT", "NEARUSDT",
    "MATICUSDT", "SHIBUSDT", "TRXUSDT", "LTCUSDT", "UNIUSDT"
]
streams = [f"{symbol.lower()}@ticker" for symbol in SYMBOLS]

prices_history = {symbol: [] for symbol in SYMBOLS}
active_positions = {}
TRADE_SIZE_USDT = 500.0   

def calculate_statistical_bounds(prices_list):
    if len(prices_list) < 20:
        return 0.0, 0.0
    mean = sum(prices_list) / len(prices_list)
    variance = sum((x - mean) ** 2 for x in prices_list) / len(prices_list)
    std_dev = math.sqrt(variance)
    return mean, std_dev

async def process_statistical_arbitrage(symbol, current_price):
    global active_positions, bot_stats, prices_history
    
    prices_history[symbol].append(current_price)
    if len(prices_history[symbol]) > 30:
        prices_history[symbol].pop(0)
        
    if symbol in active_positions:
        pos = active_positions[symbol]
        entry_price = pos['entry_price']
        price_change = (current_price - entry_price) / entry_price
        
        # 🎯 محاكاة شرط الخروج بأمر حد مرن:
        if price_change >= 0.005:  
            # حساب الأرباح بخصم عمولة BNB المخفضة الحقيقية (0.075% بدلاً من 0.1%)
            bnb_fee = TRADE_SIZE_USDT * 0.00075
            profit = (TRADE_SIZE_USDT * price_change) - bnb_fee
            
            bot_stats["total_trades"] += 1
            bot_stats["balance_usdt"] += profit
            bot_stats["net_profit_usdt"] += profit
            bot_stats["last_alert"] = f"✨ [BNB Discount Hit] قنص مربح لـ {symbol}: +{profit:.4f} USDT الصافية!"
            del active_positions[symbol]
            
        # وقف خسارة حماية 0.4%
        elif price_change <= -0.004:
            bnb_fee = TRADE_SIZE_USDT * 0.00075
            loss = (TRADE_SIZE_USDT * 0.004) + bnb_fee
            
            bot_stats["total_trades"] += 1
            bot_stats["balance_usdt"] -= loss
            bot_stats["net_profit_usdt"] -= loss
            bot_stats["last_alert"] = f"🚨 [Risk Out] تفعيل وقف الخسارة الإحصائي في {symbol} لحماية رأس المال: -{loss:.2f} USDT"
            del active_positions[symbol]
        return

    mean, std_dev = calculate_statistical_bounds(prices_history[symbol])
    if mean == 0.0 or std_dev == 0.0:
        return
        
    # رصد قيعان الانحراف المعياري الحية
    lower_bound = mean - (2.0 * std_dev)
    if current_price <= lower_bound and symbol not in active_positions:
        bot_stats["last_alert"] = f"🔍 [Scanning Signal] عملة {symbol} دخلت منطقة اقتناص إحصائي مخفض: {current_price}"
        active_positions[symbol] = {
            "entry_price": current_price,
            "amount": TRADE_SIZE_USDT
        }

async def run_hft_v5_core():
    bot_stats["status"] = "Connecting to 15 BNB-Optimized Streams..."
    client = await AsyncClient.create(API_KEY, SECRET_KEY)
    bm = BinanceSocketManager(client)
    multiplex_socket = bm.multiplex_socket(streams)
    
    bot_stats["status"] = "HFT V5 Active - 15 Assets & BNB Fees Loaded 📊"

    async with multiplex_socket as stream:
        while True:
            try:
                res = await stream.recv()
                if res and 'data' in res:
                    data = res['data']
                    symbol = data['s']
                    current_price = float(data['c'])
                    asyncio.create_task(process_statistical_arbitrage(symbol, current_price))
            except Exception:
                await asyncio.sleep(0.001)

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_hft_v5_core())
