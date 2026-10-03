import os
import asyncio
import threading
from flask import Flask
from flask_socketio import SocketIO
from binance import AsyncClient, BinanceSocketManager

# --- 1. إعداد خادم Flask مع تقنية البث المباشر للشاشة (SocketIO) ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'hft_secret!'
socketio = SocketIO(app, async_mode='gevent', cors_allowed_origins="*")

# ذاكرة سريعة لتخزين الأسعار
prices = {"BTCUSDT": 0.0, "DOTBTC": 0.0, "DOTUSDT": 0.0}
trade_lock = False

@app.route('/')
def home():
    """واجهة الرادار القديمة باللون الأسود والأسطر المتدفقة حية"""
    html = """
    <html>
        <head>
            <title>HFT V2 - Live Radar</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <script src="https://cloudflare.com"></script>
            <style>
                body { font-family: 'Courier New', monospace; background: #0c0c0c; color: #00ff00; padding: 15px; margin: 0; }
                .header { border-bottom: 1px solid #333; padding-bottom: 10px; margin-bottom: 15px; }
                .title { color: #ffcc00; font-weight: bold; font-size: 18px; }
                #log-container { width: 100%; height: 75vh; overflow-y: auto; background: #111; border: 1px solid #222; padding: 10px; border-radius: 5px; box-sizing: border-box; }
                .line { margin: 4px 0; font-size: 13px; line-height: 1.4; }
                .green { color: #00ff00; }
                .yellow { color: #ffcc00; }
                .blue { color: #00ccff; }
                .purple { color: #cc66ff; }
            </style>
        </head>
        <body>
            <div class="header">
                <div class="title">🚀 محرك HFT V2 - رادار التحكيم الثلاثي اللحظي</div>
                <div style="color: #aaa; font-size: 12px; margin-top:5px;">حالة المحرك: مستقر ويقنص بالملي ثانية 🛡️</div>
            </div>
            <div id="log-container">
                <div class="line blue">⚙️ جاري تحضير البيئة السحابية والربط ببينانس...</div>
            </div>

            <script>
                var socket = io();
                var container = document.getElementById('log-container');
                
                socket.on('radar_log', function(msg) {
                    var div = document.createElement('div');
                    div.className = 'line';
                    
                    // تلوين الأسطر بناءً على نوع الرسالة البرمجية
                    if (msg.includes('✨') || msg.includes('نجاح')) {
                        div.className = 'line green';
                    } else if (msg.includes('🔄')) {
                        div.className = 'line yellow';
                    } else if (msg.includes('📡')) {
                        div.className = 'line blue';
                    } else if (msg.includes('📈')) {
                        div.className = 'line purple';
                    }
                    
                    div.innerHTML = msg;
                    container.appendChild(div);
                    
                    // النزول التلقائي لأسفل الشاشة مع تدفق الأسطر الجديدة
                    container.scrollTop = container.scrollHeight;
                });
            </script>
        </body>
    </html>
    """
    return html

# --- 2. محرك التحكيم الثلاثي الحسابي بأجزاء الثانية ---
API_KEY = os.getenv('BINANCE_API_KEY')
SECRET_KEY = os.getenv('BINANCE_SECRET_KEY')

TRIANGLE_PAIRS = ["BTCUSDT", "DOTBTC", "DOTUSDT"]
streams = [f"{pair.lower()}@ticker" for pair in TRIANGLE_PAIRS]

def send_to_web(message):
    """إرسال السطر فوراً ليعرض على شاشة الجوال بشكل حي"""
    socketio.emit('radar_log', message)

async def check_triangular_arbitrage():
    global trade_lock
    p1 = prices["BTCUSDT"]
    p2 = prices["DOTBTC"]
    p3 = prices["DOTUSDT"]
    
    if p1 == 0.0 or p2 == 0.0 or p3 == 0.0:
        return
    if trade_lock:
        return

    simulated_return = (1.0 / p1) / p2 * p3
    net_profit_pct = (simulated_return - 1.0) * 100
    
    # قنص فرصة التحكيم الثلاثي اللحظية
    if simulated_return > 1.0001:
        trade_lock = True
        send_to_web(f"✨ [المثلث الناجح] قنص لحظي! المسار: USDT ➡️ BTC ➡️ DOT")
        send_to_web(f"📈 العائد المحاكى: {simulated_return:.6f} | الربح: +{net_profit_pct:.4f}%")
        await asyncio.sleep(0.1)
        trade_lock = False

async def run_binance_hft():
    if not API_KEY or not SECRET_KEY:
        send_to_web("❌ خطأ قاطع: لم يتم العثور على مفاتيح Binance!")
        return

    client = await AsyncClient.create(API_KEY, SECRET_KEY, testnet=True)
    bm = BinanceSocketManager(client)
    multiplex_socket = bm.multiplex_socket(streams)
    
    send_to_web("📡 رادار التحكيم الثلاثي متصل بنجاح ببث الأسعار المباشر (WebSockets)...")

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
                        # بث الأسعار اللحظية متتالية على شاشة الويب
                        send_to_web(f"🔄 [رادار حي] تحديث سعر {pair_name}: {current_close}")
                        asyncio.create_task(check_triangular_arbitrage())
            except Exception:
                await asyncio.sleep(0.2)

def start_radar_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_binance_hft())

if __name__ == "__main__":
    # 1. تشغيل رادار قنص بينانس في الخلفية
    hft_thread = threading.Thread(target=start_radar_loop, daemon=True)
    hft_thread.start()

    # 2. تشغيل خادم الويب المتطور المتوافق مع البث المباشر لـ Render
    port = int(os.environ.get("PORT", 10000))
    socketio.run(app, host="0.0.0.0", port=port)
