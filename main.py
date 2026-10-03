import os
import time
import threading
from flask import Flask
from binance.client import Client

app = Flask(__name__)

# تخزين البيانات لعرضها مباشرة
radar_data = {
    "status": "📡 الرادار متصل ويحدث الأسعار تلقائياً غصباً عن السيرفر!",
    "btc_price": "0.0",
    "dot_btc": "0.0",
    "dot_usdt": "0.0",
    "profit_msg": "🔍 جاري فحص الفجوات السعرية للمثلث الحسابي..."
}

@app.route('/')
def home():
    # صفحة HTML بسيطة تحدث نفسها قسرياً كل ثانيتين لجلب الأسعار الجديدة
    return f"""
    <html>
        <head>
            <meta http-equiv="refresh" content="2">
            <title>HFT V2 - Real Test</title>
            <style>
                body {{ font-family: monospace; background: #0a0a0a; color: #00ff00; padding: 30px; text-align: center; }}
                .container {{ border: 2px solid #333; padding: 20px; display: inline-block; background: #111; border-radius: 8px; text-align: left; }}
                h2 {{ color: #ffcc00; text-align: center; }}
                .price {{ color: #00ffff; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>🚀 محرك HFT V2 - التحكيم الثلاثي</h2>
                <p><b>الحالة:</b> {radar_data['status']}</p>
                <hr style="border-color:#222;">
                <p>💰 سعر BTCUSDT: <span class="price">{radar_data['btc_price']} USDT</span></p>
                <p>💰 سعر DOTBTC: <span class="price">{radar_data['dot_btc']} BTC</span></p>
                <p>💰 سعر DOTUSDT: <span class="price">{radar_data['dot_usdt']} USDT</span></p>
                <hr style="border-color:#222;">
                <p>🎯 <b>النتيجة اللحظية:</b> {radar_data['profit_msg']}</p>
            </div>
        </body>
    </html>
    """

def run_arbitrage_loop():
    """محرك تقليدي صلب يطلب الأسعار كل ثانيتين بدون تعقيد Async"""
    api_key = os.getenv('BINANCE_API_KEY')
    secret_key = os.getenv('BINANCE_SECRET_KEY')
    
    try:
        # الاتصال التقليدي المباشر
        client = Client(api_key, secret_key, testnet=True)
        
        while True:
            try:
                # جلب الأسعار اللحظية بشكل مباشر وتتابعي
                btc_usdt = float(client.get_symbol_ticker(symbol="BTCUSDT")['price'])
                dot_btc = float(client.get_symbol_ticker(symbol="DOTBTC")['price'])
                dot_usdt = float(client.get_symbol_ticker(symbol="DOTUSDT")['price'])
                
                # تحديث الذاكرة فوراً
                radar_data["btc_price"] = str(btc_usdt)
                radar_data["dot_btc"] = str(dot_btc)
                radar_data["dot_usdt"] = str(dot_usdt)
                
                # حساب معادلة التحكيم الثلاثي للمثلث (USDT -> BTC -> DOT -> USDT)
                simulated_return = (1.0 / btc_usdt) / dot_btc * dot_usdt
                net_profit = (simulated_return - 1.0) * 100
                
                if simulated_return > 1.0001:
                    radar_data["profit_msg"] = f"✨ [مثلث ناجح] تم قنص فجوة ربح بقيمة: +{net_profit:.4f}% 🎉"
                else:
                    radar_data["profit_msg"] = f"🔍 فحص مستمر... العائد الحالي: {net_profit:.4f}% (لا يوجد فجوة مربحة)"
                    
            except Exception as e:
                radar_data["status"] = f"⚠️ خطأ أثناء تحديث الأسعار: {str(e)}"
                
            time.sleep(2) # انتظر ثانيتين ثم كرر الطلب المباشر
    except Exception as e:
        radar_data["status"] = f"❌ فشل الاتصال الأولي ببينانس: {str(e)}"

if __name__ == "__main__":
    # تشغيل المحرك المباشر في الخلفية
    t = threading.Thread(target=run_arbitrage_loop, daemon=True)
    t.start()
    
    # تشغيل خادم الويب على المنفذ المطلوب
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, use_reloader=False)
