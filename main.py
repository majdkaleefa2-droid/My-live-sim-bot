import os
import time
import asyncio
import threading
from flask import Flask
from binance import AsyncClient, BinanceSocketManager

# --- 1. إعداد خادم Flask المستقل لإرضاء Render ---
app = Flask(__name__)

@app.route('/')
def home():
    return "🚀 HFT V2 Engine is Fully Active 🚀"

def start_flask():
    port = int(os.environ.get("PORT", 10000))
    # تشغيل Flask بدون ميزات التتبع الإضافية لضمان الخفة
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

# --- 2. محرك التحكيم الثلاثي الاحترافي والمفاتيح ---
API_KEY = os.getenv('BINANCE_API_KEY')
SECRET_KEY = os.getenv('BINANCE_SECRET_KEY')

# أزواج المثلث المعتمد (USDT -> BTC -> DOT -> USDT)
TRIANGLE_PAIRS = ["BTCUSDT", "DOTBTC", "DOTUSDT"]
streams = [f"{pair.lower()}@ticker" for pair in TRIANGLE_PAIRS]

prices = {pair: 0.0 for pair in TRIANGLE_PAIRS}
trade_lock = False

async def check_triangular_arbitrage():
    global trade_lock
    p1 = prices["BTCUSDT"]
    p2 = prices["DOTBTC"]
    p3 = prices["DOTUSDT"]
    
    if p1 == 0.0 or p2 == 0.0 or p3 == 0.0:
        return
    if trade_lock:
        return

    # معادلة التحكيم الثلاثي بأجزاء الثانية
    simulated_return = (1.0 / p1) / p2 * p3
    net_profit_pct = (simulated_return - 1.0) * 100
    
    if simulated_return > 1.0001:
        trade_lock = True
        print(f"✨ [المثلث الناجح] قنص لحظي بالملي ثانية | المسار: USDT ➡️ BTC ➡️ DOT")
        print(f"📈 العائد المحاكى: {simulated_return:.6f} | الربح المتوقع: +{net_profit_pct:.4f}%")
        await asyncio.sleep(0.1)
        trade_lock = False

async def run_binance_hft():
    print("🚀 محرك (HFT V2) يبدأ الاتصال الآن بالشبكة التجريبية...")
    
    if not API_KEY or not SECRET_KEY:
        print("❌ خطأ قاطع: لم يتم العثور على مفاتيح Binance الحساسة!")
        return

    # إنشاء الاتصال غير المتزامن المستقل تماماً
    client = await AsyncClient.create(API_KEY, SECRET_KEY, testnet=True)
    bm = BinanceSocketManager(client)
    multiplex_socket = bm.multiplex_socket(streams)
    
    print("📡 رادار التحكيم الثلاثي متصل ببث الأسعار المباشر (WebSockets) بنجاح!")

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
                        
                        # سطر الإثبات البصري الفوري لتدفق الأسعار
                        print(f"🔄 [رادار حي] تحديث سعر {pair_name}: {current_close} USDT")
                        
                        asyncio.create_task(check_triangular_arbitrage())
            except Exception as e:
                await asyncio.sleep(0.5)

def start_radar_loop():
    """تأسيس خط أحداث (Event Loop) مستقل ونظيف تماماً للرادار وبينانس"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_binance_hft())

if __name__ == "__main__":
    print("⚙️ جاري تشغيل المحرك المالي والويب معاً بنظام العزل...")
    
    # 1. إطلاق خادم Flask في خيط مستقل فوراً ليمسك بالـ Port
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()
    
    # إعطاء خادم الويب ثانية واحدة ليستقر
    time.sleep(1)

    # 2. إطلاق رادار بينانس في الخيط الرئيسي لضمان عدم حظره نهائياً
    start_radar_loop()
