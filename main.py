import os
from flask import Flask
from binance.client import Client

app = Flask(__name__)

# دعم طلبات HEAD و GET معاً لمنع خطأ 405 نهائياً في ريندر
@app.route('/', methods=['GET', 'HEAD'])
def home():
    # جلب المفاتيح مباشرة من إعدادات ريندر
    api_key = os.getenv('BINANCE_API_KEY')
    secret_key = os.getenv('BINANCE_SECRET_KEY')
    
    try:
        # الاتصال المباشر والتقليدي ببينانس
        client = Client(api_key, secret_key, testnet=True)
        
        # جلب الأسعار اللحظية في نفس ثانية طلب الصفحة
        btc_usdt = float(client.get_symbol_ticker(symbol="BTCUSDT")['price'])
        dot_btc = float(client.get_symbol_ticker(symbol="DOTBTC")['price'])
        dot_usdt = float(client.get_symbol_ticker(symbol="DOTUSDT")['price'])
        
        # حساب معادلة التحكيم الثلاثي للمثلث (USDT -> BTC -> DOT -> USDT)
        simulated_return = (1.0 / btc_usdt) / dot_btc * dot_usdt
        net_profit = (simulated_return - 1.0) * 100
        
        if simulated_return > 1.0001:
            profit_msg = f"<span style='color: #5cb85c;'>✨ [مثلث ناجح] تم قنص فجوة ربح: +{net_profit:.4f}% 🎉</span>"
        else:
            profit_msg = f"<span style='color: #aaa;'>🔍 فحص مستمر... العائد الحالي: {net_profit:.4f}%</span>"
            
        status_msg = "📡 الرادار متصل ويجلب الأسعار مباشرة من بينانس بنجاح!"
        
    except Exception as e:
        btc_usdt = dot_btc = dot_usdt = 0.0
        status_msg = f"⚠️ خطأ في الاتصال أو المفاتيح: {str(e)}"
        profit_msg = "يرجى التحقق من صحة الـ API Key والـ Secret Key في Render."

    # صفحة HTML نظيفة تحدث نفسها تلقائياً كل ثانيتين قسرياً لعرض تحديث الأسعار
    return f"""
    <html>
        <head>
            <meta http-equiv="refresh" content="2">
            <title>HFT V2 - Live Check</title>
            <style>
                body {{ font-family: monospace; background: #0c0c0c; color: #00ff00; padding: 30px; text-align: center; }}
                .container {{ border: 2px solid #222; padding: 25px; display: inline-block; background: #111; border-radius: 8px; text-align: left; min-width: 350px; }}
                h2 {{ color: #ffcc00; text-align: center; margin-top: 0; }}
                .price {{ color: #00ffff; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>🚀 محرك HFT V2 - الرادار المباشر</h2>
                <p><b>حالة السيرفر:</b> {status_msg}</p>
                <hr style="border-color:#222;">
                <p>💰 سعر BTCUSDT: <span class="price">{btc_usdt} USDT</span></p>
                <p>💰 سعر DOTBTC: <span class="price">{dot_btc} BTC</span></p>
                <p>💰 سعر DOTUSDT: <span class="price">{dot_usdt} USDT</span></p>
                <hr style="border-color:#222;">
                <p>🎯 <b>نتيجة القنص اللحظية:</b> {profit_msg}</p>
            </div>
        </body>
    </html>
    """

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, use_reloader=False)
