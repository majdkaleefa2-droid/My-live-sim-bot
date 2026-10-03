import os
from flask import Flask
from binance.client import Client

app = Flask(__name__)

@app.route('/', methods=['GET', 'HEAD'])
def home():
    api_key = os.getenv('BINANCE_API_KEY')
    secret_key = os.getenv('BINANCE_SECRET_KEY')
    
    try:
        # 💡 التعديل الجوهري: حذفنا (testnet=True) عند قراءة الأسعار لجلب السوق الحقيقي اللحظي مجاناً وبأمان 100%
        client = Client(api_key, secret_key)
        
        # جلب الأسعار الحقيقية اللحظية من السوق الآن
        btc_usdt = float(client.get_symbol_ticker(symbol="BTCUSDT")['price'])
        dot_btc = float(client.get_symbol_ticker(symbol="DOTBTC")['price'])
        dot_usdt = float(client.get_symbol_ticker(symbol="DOTUSDT")['price'])
        
        # معادلة التحكيم الثلاثي للمثلث (USDT -> BTC -> DOT -> USDT)
        simulated_return = (1.0 / btc_usdt) / dot_btc * dot_usdt
        net_profit = (simulated_return - 1.0) * 100
        
        if simulated_return > 1.0001:
            profit_msg = f"<span style='color: #5cb85c;'>✨ [مثلث ناجح] تم قنص فجوة ربح حقيقية: +{net_profit:.4f}% 🎉</span>"
        else:
            profit_msg = f"<span style='color: #aaa;'>🔍 فحص مستمر للسوق الحقيقي... العائد الحالي: {net_profit:.4f}%</span>"
            
        status_msg = "📡 الرادار متصل ويقنص أسعار السوق الحقيقي اللحظي بنجاح!"
        
    except Exception as e:
        btc_usdt = dot_btc = dot_usdt = 0.0
        status_msg = f"⚠️ خطأ في الاتصال: {str(e)}"
        profit_msg = "يرجى التحقق من الاتصال."

    return f"""
    <html>
        <head>
            <meta http-equiv="refresh" content="2">
            <title>HFT V2 - Live Mainnet</title>
            <style>
                body {{ font-family: monospace; background: #0c0c0c; color: #00ff00; padding: 30px; text-align: center; }}
                .container {{ border: 2px solid #222; padding: 25px; display: inline-block; background: #111; border-radius: 8px; text-align: left; min-width: 350px; }}
                h2 {{ color: #ffcc00; text-align: center; margin-top: 0; }}
                .price {{ color: #00ffff; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>🚀 محرك HFT V2 - الرادار الحقيقي</h2>
                <p><b>حالة السيرفر:</b> {status_msg}</p>
                <hr style="border-color:#222;">
                <p>💰 سعر BTCUSDT: <span class="price">{btc_usdt} USDT</span></p>
                <p>💰 سعر DOTBTC: <span class="price">{dot_btc:.6f} BTC</span></p>
                <p>💰 سعر DOTUSDT: <span class="price">{dot_usdt} USDT</span></p>
                <hr style="border-color:#222;">
                <p>🎯 <b>نتيجة القنص الحية:</b> {profit_msg}</p>
            </div>
        </body>
    </html>
    """

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, use_reloader=False)
