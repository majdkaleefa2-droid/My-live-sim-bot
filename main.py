import os
import asyncio
import threading
from flask import Flask
from binance import AsyncClient, BinanceSocketManager

app = Flask(__name__)

# لوحة القيادة المالية المتقدمة V4
bot_stats = {
    "status": "⚙️ Booting HFT Enterprise V4...",
    "balance_usdt": 10000.0,
    "net_profit_usdt": 0.0,
    "total_trades": 0,
    "last_alert": "System checking indicators and market rules..."
}

@app.route('/')
def home():
    html = f"""
    <html>
        <head>
            <meta http-equiv="refresh" content="1">
            <title>HFT Core V4 - Multi-Asset System</title>
            <style>
                body {{ font-family: 'Courier New', monospace; background: #050505; color: #00ff00; padding: 20px; text-align: center; }}
                .dashboard {{ border: 2px solid #00ff00; padding: 25px; display: inline-block; background: #111; border-radius: 8px; text-align: left; min-width: 500px; box-shadow: 0 0 20px rgba(0,255,0,0.3); }}
                h2 {{ color: #ffcc00; text-align: center; margin-top: 0; }}
                .metric {{ color: #00ffff; font-weight: bold; }}
                .status {{ color: #5cb85c; font-weight: bold; }}
                .profit {{ color: #5cb85c; font-weight: bold; }}
                .danger {{ color: #d9534f; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="dashboard">
                <h2>🎛️ نظام HFT المؤسساتي الشامل - V4</h2>
                <p><b>حالة النظام العام:</b> <span class="status">{bot_stats['status']}</span></p>
                <div style="font-size:11px; color:#aaa; margin-bottom:10px;">⏰ درع الاستيقاظ النشط (Anti-Sleep): شغال 🟢</div>
                <hr style="border-color: #222;">
                <p>💵 إجمالي رأس المال: <span class="metric">{bot_stats['balance_usdt']:.2f} USDT</span></p>
                <p>📈 صافي الأرباح المحققة: <span class="{'profit' if bot_stats['net_profit_usdt'] >= 0 else 'danger'}">{bot_stats['net_profit_usdt']:.4f} USDT</span></p>
                <p>🔄 الصفقات المنفذة بالقوانين: <span class="metric">{bot_stats['total_trades']} صفقة</span></p>
                <hr style="border-color: #222;">
                <p>🚨 <b>آخر إشعار من الرادار والمؤشرات:</b> <br><span style="color: #ffcc00; font-size: 12px;">{bot_stats['last_alert']}</span></p>
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

# مراقبة الأصول الساخنة الكبرى في السوق الحقيقي
SYMBOLS = ["BTCUSDT", "SOLUSDT", "ETHUSDT"]
streams = [f"{symbol.lower()}@ticker" for symbol in SYMBOLS]

prices_history = {symbol: [] for symbol in SYMBOLS}
active_positions = {}

# إعدادات المخاطر وأوامر الـ Stop Loss والـ Limit
TRADE_SIZE_USDT = 500.0   
STOP_LOSS_RULE = 0.005     # وقف خسارة صارم عند 0.5% لحماية رأس المال
LIMIT_PROFIT_RULE = 0.01   # جني أرباح مستهدف بأمر حد عند صعود 1%

def calculate_rsi(prices_list, period=14):
    """محرك حساب مؤشر RSI مدمج وسريع جداً لأجزاء الثانية"""
    if len(prices_list) < period + 1:
        return 50.0  # قيمة حيادية إذا كانت البيانات غير كافية
    
    gains = []
    losses = []
    for i in range(len(prices_list) - period, len(prices_list)):
        diff = prices_list[i] - prices_list[i-1]
        if diff >= 0:
            gains.append(diff)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(diff))
            
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))

async def process_advanced_market_rules(symbol, current_price):
    global active_positions, bot_stats, prices_history
    
    # تحديث التاريخ السعري لحساب المؤشرات
    prices_history[symbol].append(current_price)
    if len(prices_history[symbol]) > 50:
        prices_history[symbol].pop(0)
        
    # 1) إدارة الصفقات المفتوحة (تطبيق قوانين الـ Stop Loss والـ Limit)
    if symbol in active_positions:
        pos = active_positions[symbol]
        entry_price = pos['entry_price']
        price_change = (current_price - entry_price) / entry_price
        
        # أ) قانون أمر الحد لجني الأرباح (Limit Order) خصم العمولات 0.1%
        if price_change >= LIMIT_PROFIT_RULE:
            profit = (TRADE_SIZE_USDT * LIMIT_PROFIT_RULE) - (TRADE_SIZE_USDT * 0.001)
            bot_stats["total_trades"] += 1
            bot_stats["balance_usdt"] += profit
            bot_stats["net_profit_usdt"] += profit
            bot_stats["last_alert"] = f"💰 [Limit Order Hit] تم بيع {symbol} بربح صافي: +{profit:.2f} USDT 🎉"
            del active_positions[symbol]
            
        # ب) قانون وقف الخسارة الصارم (Stop Loss Rule)
        elif price_change <= -STOP_LOSS_RULE:
            loss = (TRADE_SIZE_USDT * STOP_LOSS_RULE) + (TRADE_SIZE_USDT * 0.001)
            bot_stats["total_trades"] += 1
            bot_stats["balance_usdt"] -= loss
            bot_stats["net_profit_usdt"] -= loss
            bot_stats["last_alert"] = f"🚨 [Stop Loss Triggered] الخروج من {symbol} لحماية المحفظة عند خسارة: -{loss:.2f} USDT"
            del active_positions[symbol]
        return

    # 2) حساب مؤشر RSI اللحظي لاتخاذ قرار الدخول بأمر حد
    rsi_value = calculate_rsi(prices_history[symbol])
    
    # إشارة الدخول: إذا كان الـ RSI تحت 30 (تشبع بيعي وقاع ممتاز للشراء)
    if rsi_value < 30.0 and symbol not in active_positions:
        # وضع أمر حد للشراء (Limit Buy) تحت سعر السوق بـ 0.05% لاقتناص السعر بدقة
        limit_buy_price = current_price * 0.9995
        
        bot_stats["last_alert"] = f"🛒 [RSI={rsi_value:.1f}] تعليق أمر شراء حد لـ {symbol} عند سعر {limit_buy_price:.2f}"
        
        active_positions[symbol] = {
            "entry_price": limit_buy_price,
            "amount": TRADE_SIZE_USDT
        }

async def run_hft_v4_core():
    bot_stats["status"] = "Connecting to Live WebSockets..."
    client = await AsyncClient.create(API_KEY, SECRET_KEY)
    bm = BinanceSocketManager(client)
    multiplex_socket = bm.multiplex_socket(streams)
    
    bot_stats["status"] = "HFT V4 Active - RSI & Limit Rules Enabled ⚡"

    async with multiplex_socket as stream:
        while True:
            try:
                res = await stream.recv()
                if res and 'data' in res:
                    data = res['data']
                    symbol = data['s']
                    current_price = float(data['c'])
                    
                    asyncio.create_task(process_advanced_market_rules(symbol, current_price))
            except Exception:
                await asyncio.sleep(0.001)

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_hft_v4_core())
