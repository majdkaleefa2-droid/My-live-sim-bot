import os
import asyncio
import threading
from flask import Flask, jsonify
from binance import AsyncClient, BinanceSocketManager

# --- 1. إعداد خادم Flask الذكي لعرض العمليات حية ---
app = Flask(__name__)

# ذاكرة سريعة لتخزين حالة الرادار والأسعار اللحظية
radar_status = {
    "status": "⚙️ جاري تحضير المحرك...",
    "pairs": {"BTCUSDT": 0.0, "DOTBTC": 0.0, "DOTUSDT": 0.0},
    "last_opportunity": "لم يتم رصد فرصة بعد",
    "profit_log": []
}

@app.route('/')
def home():
    """صفحة الويب الرئيسية التي ستفتحها لتضمن أن البوت يعمل 100%"""
    html = f"""
    <html>
        <head>
            <meta http-equiv="refresh" content="1"> <!-- إعادة تحميل تلقائي كل ثانية -->
            <title>HFT V2 Control Panel</title>
            <style>
                body {{ font-family: Arial, sans-serif; background: #121212; color: #fff; text-align: center; padding-top: 50px; }}
                .box {{ border: 2px solid #0275d8; padding: 20px; display: inline-block; border-radius: 10px; background: #1a1a1a; min-width: 300px; }}
                h1 {{ color: #0275d8; }}
                .green {{ color: #5cb85c; font-weight: bold; }}
                .yellow {{ color: #f0ad4e; }}
            </style>
        </head>
        <body>
            <div class="box">
                <h1>🚀 محرك HFT V2 اللحظي</h1>
                <p><b>حالة الاتصال:</b> <span class="green">{radar_status['status']}</span></p>
                <hr style="border-color: #333;">
                <h3>📊 الأسعار الحية من بينانس:</h3>
                <p>BTCUSDT: <span class="yellow">{radar_status['pairs']['BTCUSDT']} USDT</span></p>
                <p>DOTBTC: <span class="yellow">{radar_status['pairs']['DOTBTC']} BTC</span></p>
                <p>DOTUSDT: <span class="yellow">{radar_status['pairs']['DOTUSDT']} USDT</span></p>
                <hr style="border-color: #333;">
                <h3>🎯 آخر قنص للمثلث:</h3>
                <p>{radar_status['last_opportunity']}</p>
            </div>
        </body>
    </html>
    """
    return html

def run_flask_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, use_reloader=False)

# --- 2. محرك التحكيم الثلاثي لـ Binance Testnet ---
API_KEY = os.getenv('BINANCE_API_KEY')
SECRET_KEY = os.getenv('BINANCE_SECRET_KEY')

TRIANGLE_PAIRS = ["BTCUSDT", "DOTBTC", "DOTUSDT"]
streams = [f"{pair.lower()}@ticker" for pair in TRIANGLE_PAIRS]
trade_lock = False

async def check_triangular_arbitrage():
    global trade_lock
    p1 = radar_status['pairs']["BTCUSDT"]
    p2 = radar_status['pairs']["DOTBTC"]
    p3 = radar_status['pairs']["DOTUSDT"]
    
    if p1 == 0.0 or p2 == 0.0 or p3 == 0.0:
        return
    if trade_lock:
        return

    simulated_return = (1.0 / p1) / p2 * p3
    net_profit_pct = (simulated_return - 1.0) * 100
    
    if simulated_return > 1.0001:
        trade_lock = True
        msg = f"✨ قنص ناجح! المسار: USDT ➡️ BTC ➡️ DOT | الربح: +{net_profit_pct:.4f}%"
        radar_status['last_opportunity'] = msg
        await asyncio.sleep(0.2)
        trade_lock = False

async def run_binance_hft():
    radar_status['status'] = "🔄 جاري الاتصال ببث بينانس..."
    if not API_KEY or not SECRET_KEY:
        radar_status['status'] = "❌ خطأ: لم يتم العثور على المفاتيح!"
        return

    client = await AsyncClient.create(API_KEY, SECRET_KEY, testnet=True)
    bm = BinanceSocketManager(client)
    multiplex_socket = bm.multiplex_socket(streams)
    
    radar_status['status'] = "📡 الرادار متصل ويقنص الأسعار حالياً!"

    async with multiplex_socket as stream:
        while True:
            try:
                res = await stream.recv()
                if res and 'data' in res:
                    data = res['data']
                    pair_name = data['s']
                    current_close = float(data['c'])
                    
                    if pair_name in radar_status['pairs']:
                        # تحديث السعر في الذاكرة المعروضة على الويب فوراً
                        radar_status['pairs'][pair_name] = current_close
                        asyncio.create_task(check_triangular_arbitrage())
            except Exception:
                await asyncio.sleep(0.5)

def start_hft_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_binance_hft())

if __name__ == "__main__":
    # 1. تشغيل رادار بينانس في خيط مستقل
    hft_thread = threading.Thread(target=start_hft_loop, daemon=True)
    hft_thread.start()

    # 2. تشغيل خادم ويب Flask
    run_flask_server()
