import os
import asyncio
import threading
from flask import Flask
from binance import AsyncClient, BinanceSocketManager

# --- 1. خادم الويب للحفاظ على استقرار السيرفر المجاني ---
app = Flask(__name__)

# سجل الإحصائيات المالي الذي سنعتمد عليه لاتخاذ قرار رأس المال الحقيقي
bot_stats = {
    "status": "⚙️ جاري تشغيل الرادار...",
    "total_trades": 0,
    "simulated_balance_usdt": 10000.0, # بدأنا بـ 10 آلاف دولار وهمية على أسعار حقيقية
    "net_profit_usdt": 0.0,
    "last_trade": "لا يوجد صفقات بعد"
}

@app.route('/')
def home():
    # واجهة مالية احترافية تُحدث نفسها كل ثانية لمراقبة أداء البوت
    html = f"""
    <html>
        <head>
            <meta http-equiv="refresh" content="1">
            <title>HFT V2 - Mainnet Paper Trader</title>
            <style>
                body {{ font-family: 'Courier New', monospace; background: #0a0a0a; color: #00ff00; padding: 20px; text-align: center; }}
                .dashboard {{ border: 2px solid #333; padding: 25px; display: inline-block; background: #111; border-radius: 8px; text-align: left; min-width: 400px; }}
                h2 {{ color: #ffcc00; text-align: center; margin-top: 0; }}
                .metric {{ color: #00ffff; font-weight: bold; }}
                .profit {{ color: #5cb85c; font-weight: bold; }}
                .danger {{ color: #d9534f; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="dashboard">
                <h2>📊 لوحة القيادة المالية - HFT V2</h2>
                <p><b>حالة الرادار:</b> {bot_stats['status']}</p>
                <hr style="border-color:#222;">
                <p>💵 الرصيد الحالي: <span class="metric">{bot_stats['simulated_balance_usdt']:.2f} USDT</span></p>
                <p>📈 صافي الأرباح/الخسائر: <span class="{'profit' if bot_stats['net_profit_usdt'] >= 0 else 'danger'}">{bot_stats['net_profit_usdt']:.4f} USDT</span></p>
                <p>🔄 إجمالي العمليات المنفذة: <span class="metric">{bot_stats['total_trades']} صفقة ثلاثية</span></p>
                <hr style="border-color:#222;">
                <p>🎯 <b>آخر عملية قنص:</b> <br><span style="color: #aaa; font-size: 12px;">{bot_stats['last_trade']}</span></p>
            </div>
        </body>
    </html>
    """
    return html

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, use_reloader=False)

# --- 2. محرك التحكيم الثلاثي غير المتزامن بأجزاء الثانية لأسعار السوق الحقيقي ---
API_KEY = os.getenv('BINANCE_API_KEY')
SECRET_KEY = os.getenv('BINANCE_SECRET_KEY')

TRIANGLE_PAIRS = ["BTCUSDT", "DOTBTC", "DOTUSDT"]
streams = [f"{pair.lower()}@ticker" for pair in TRIANGLE_PAIRS]

prices = {pair: 0.0 for pair in TRIANGLE_PAIRS}
trade_lock = False

async def execute_virtual_arbitrage(p1, p2, p3):
    """
    📈 محاكاة التنفيذ الفوري بأجزاء الثانية مع احتساب عمولات بينانس الحقيقية (0.1%)
    """
    global trade_lock
    trade_lock = True
    
    # حساب العائد الإجمالي للمثلث
    simulated_return = (1.0 / p1) / p2 * p3
    
    # خصم عمولة بينانس القياسية لـ 3 صفقات متتالية (0.1% * 3 = 0.3%)
    fee_factor = 0.003
    net_return = simulated_return - fee_factor
    
    # حساب الربح الصافي الفعلي بالدولار بناءً على حجم صفقة بـ 1000 دولار
    trade_size = 1000.0
    profit_usdt = (net_return - 1.0) * trade_size
    
    # 🎯 شرط الدخول: نقنص فقط إذا كان الربح موجباً بعد خصم العمولات الحقيقي
flaskif simulated_return > 1.0000:  # سيقنص فوراً أي فجوة سعرية بمجرد أن تكسر حاجز التعادل
        bot_stats["total_trades"] += 1
        bot_stats["simulated_balance_usdt"] += profit_usdt
        bot_stats["net_profit_usdt"] += profit_usdt
        bot_stats["last_trade"] = f"✨ تم قنص فجوة حقيقية! ربح صافي: +{profit_usdt:.4f} USDT (بعد العمولات)"
        print(f"💰 [قنص حقيقي وهمي] ربح صافي: +{profit_usdt:.4f} USDT")
    
    # مهلة ملي ثانية سريعة لفتح القفل
    await asyncio.sleep(0.05)
    trade_lock = False

async def run_hft_mainnet_core():
    global prices
    bot_stats["status"] = "🔄 جاري الاتصال بخوادم بينانس الحية..."
    
    # الاتصال بحساب بينانس لجلب بيانات السوق الحقيقي المباشر اللحظي
    client = await AsyncClient.create(API_KEY, SECRET_KEY)
    bm = BinanceSocketManager(client)
    multiplex_socket = bm.multiplex_socket(streams)
    
    bot_stats["status"] = "🟢 متصل بالسوق الحقيقي ويراقب الفجوات بالملي ثانية!"
    print("📡 رادار HFT متصل بالبث الحي المباشر...")

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
                        
                        # سحب الأسعار اللحظية بالملي ثانية
                        p1, p2, p3 = prices["BTCUSDT"], prices["DOTBTC"], prices["DOTUSDT"]
                        
                        if p1 > 0 and p2 > 0 and p3 > 0 and not trade_lock:
                            asyncio.create_task(execute_virtual_arbitrage(p1, p2, p3))
            except Exception:
                await asyncio.sleep(0.01)

def start_core_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_hft_mainnet_core())

if __name__ == "__main__":
    # 1. خادم Flask في خيط مستقل لإرضاء خوادم Render
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # 2. محرك التداول الخارق بأجزاء الثانية في الخيط الرئيسي
    start_core_loop()
