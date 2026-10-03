import os
import asyncio
import threading
from flask import Flask
from binance import AsyncClient, BinanceSocketManager

app = Flask(__name__)

# لوحة القيادة المالية المتطورة لتتبع أداء الـ 4 مثلثات معاً
bot_stats = {
    "status": "⚙️ Booting HFT Core V3...",
    "total_trades": 0,
    "simulated_balance_usdt": 10000.0,
    "net_profit_usdt": 0.0,
    "last_trade": "No enterprise trades captured yet"
}

@app.route('/')
def home():
    html = f"""
    <html>
        <head>
            <meta http-equiv="refresh" content="1">
            <title>HFT Core V3 - Enterprise Dashboard</title>
            <style>
                body {{ font-family: 'Courier New', monospace; background: #080808; color: #00ff00; padding: 20px; text-align: center; }}
                .dashboard {{ border: 2px solid #00ff00; padding: 25px; display: inline-block; background: #111; border-radius: 8px; text-align: left; min-width: 450px; box-shadow: 0 0 15px rgba(0,255,0,0.2); }}
                h2 {{ color: #ffcc00; text-align: center; margin-top: 0; }}
                .metric {{ color: #00ffff; font-weight: bold; }}
                .profit {{ color: #5cb85c; font-weight: bold; }}
                .danger {{ color: #d9534f; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="dashboard">
                <h2>📊 لوحة القيادة المؤسساتية - HFT Core V3</h2>
                <p><b>حالة نظام الرادار:</b> <span class="profit">{bot_stats['status']}</span></p>
                <hr style="border-color:#222;">
                <p>💵 رصيد المحفظة الحالي: <span class="metric">{bot_stats['simulated_balance_usdt']:.2f} USDT</span></p>
                <p>📈 صافي أرباح المحرك الصافية: <span class="{'profit' if bot_stats['net_profit_usdt'] >= 0 else 'danger'}">{bot_stats['net_profit_usdt']:.4f} USDT</span></p>
                <p>🔄 العمليات الناجحة المفلترة: <span class="metric">{bot_stats['total_trades']} صفقة ثلاثية</span></p>
                <hr style="border-color:#222;">
                <p>🎯 <b>آخر قنص فلتره درع الأمان:</b> <br><span style="color: #aaa; font-size: 12px;">{bot_stats['last_trade']}</span></p>
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

# مراقبة جميع الأزواج المطلوبة لتغطية الـ 4 مثلثات معاً في نفس أجزاء الثانية
ALL_PAIRS = ["BTCUSDT", "DOTBTC", "DOTUSDT", "SOLBTC", "SOLUSDT", "XRPBTC", "XRPUSDT", "ETHBTC", "ETHUSDT"]
streams = [f"{pair.lower()}@ticker" for pair in ALL_PAIRS]

prices = {pair: 0.0 for pair in ALL_PAIRS}
trade_lock = False

async def evaluate_triangle(name, p_btc, p_alt_btc, p_alt_usdt):
    """
    📊 الفحص الحسابي المتطور للمثلث مع تفعيل درع الأمان والانزلاق السعري
    """
    global trade_lock
    if p_btc == 0 or p_alt_btc == 0 or p_alt_usdt == 0 or trade_lock:
        return

    # 1. حساب العائد الإجمالي الأولي للمثلث
    simulated_return = (1.0 / p_btc) / p_alt_btc * p_alt_usdt
    
    # 2. احتساب عمولة بينانس الصارمة (0.1% * 3 صفقة = 0.3%) + خصم انزلاق سعري أمان لحساب تأخر التنفيذ (0.05%)
    total_deductions = 0.003 + 0.0005 
    net_return = simulated_return - total_deductions
    
    trade_size = 1000.0  # حجم رأس مال محاكاة الصفقة
    profit_usdt = (net_return - 1.0) * trade_size
    
    # 🎯 درع الأمان الفولاذي: لا يدخل إلا إذا كان الربح صافياً وموجباً بعد خصم العمولات والانزلاق بالكامل
    if profit_usdt > 0.0:
        trade_lock = True
        bot_stats["total_trades"] += 1
        bot_stats["simulated_balance_usdt"] += profit_usdt
        bot_stats["net_profit_usdt"] += profit_usdt
        bot_stats["last_trade"] = f"✨ قنص مؤسساتي ناجح بمثلث [{name}]! الربح الصافي: +{profit_usdt:.4f} USDT"
        await asyncio.sleep(0.05)  # مهلة قفل الملي ثانية لحماية التنفيذ
        trade_lock = False

async def run_hft_enterprise_core():
    global prices
    bot_stats["status"] = "Connecting to Mainnet WebSockets..."
    
    client = await AsyncClient.create(API_KEY, SECRET_KEY)
    bm = BinanceSocketManager(client)
    multiplex_socket = bm.multiplex_socket(streams)
    
    bot_stats["status"] = "HFT Core V3 Active - 4 Triangles Under Radar 📡"

    async with multiplex_socket as stream:
        while True:
            try:
                res = await stream.recv()
                if res and 'data' in res:
                    data = res['data']
                    pair_name = data['s']
                    current_close = float(data['c'])
                    
                    if pair_name in prices:
                        prices[pair_name] = current_close
                        
                        # سحب الأسعار اللحظية بالملي ثانية لتغذية الـ 4 مثلثات معاً بشكل متوازٍ
                        p_btc = prices["BTCUSDT"]
                        
                        # فحص مثلث الـ DOT
                        asyncio.create_task(evaluate_triangle("BTC-DOT", p_btc, prices["DOTBTC"], prices["DOTUSDT"]))
                        # فحص مثلث الـ SOL
                        asyncio.create_task(evaluate_triangle("BTC-SOL", p_btc, prices["SOLBTC"], prices["SOLUSDT"]))
                        # فحص مثلث الـ XRP
                        asyncio.create_task(evaluate_triangle("BTC-XRP", p_btc, prices["XRPBTC"], prices["XRPUSDT"]))
                        # فحص مثلث الـ ETH
                        asyncio.create_task(evaluate_triangle("BTC-ETH", p_btc, prices["ETHBTC"], prices["ETHUSDT"]))
            except Exception:
                await asyncio.sleep(0.001)  # تسريع الاستجابة لأعلى دقة ملي ثانية

def start_enterprise_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_hft_enterprise_core())

if __name__ == "__main__":
    # 1. تشغيل خادم ويب Flask في خلفية معزولة
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # 2. تشغيل محرك أجزاء الثانية المؤسساتي الخارق في الخط الرئيسي
    start_enterprise_loop()
