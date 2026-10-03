import os
from binance.client import Client
import tornado.ioloop
import tornado.web

# الذاكرة السريعة لتحديث وعرض البيانات
radar_data = {
    "btc": "0.0",
    "dot_btc": "0.0",
    "dot_usdt": "0.0",
    "msg": "🔍 جاري فحص فرص التحكيم الثلاثي..."
}

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        # جلب المفاتيح الحقيقية المخزنة في إعدادات ريندر
        api_key = os.getenv('BINANCE_API_KEY')
        secret_key = os.getenv('BINANCE_SECRET_KEY')
        
        try:
            # الاتصال الفوري المباشر ببينانس تجريبي
            client = Client(api_key, secret_key, testnet=True)
            
            # جلب الأسعار اللحظية بشكل تتابعي حاد
            btc_price = float(client.get_symbol_ticker(symbol="BTCUSDT")['price'])
            dot_btc = float(client.get_symbol_ticker(symbol="DOTBTC")['price'])
            dot_usdt = float(client.get_symbol_ticker(symbol="DOTUSDT")['price'])
            
            # حساب معادلة التحكيم الثلاثي للمثلث (USDT -> BTC -> DOT -> USDT)
            simulated_return = (1.0 / btc_price) / dot_btc * dot_usdt
            net_profit = (simulated_return - 1.0) * 100
            
            radar_data["btc"] = str(btc_price)
            radar_data["dot_btc"] = str(dot_btc)
            radar_data["dot_usdt"] = str(dot_usdt)
            
            if simulated_return > 1.0001:
                radar_data["msg"] = f"✨ [مثلث ناجح] قنص فجوة ربح بقيمة: +{net_profit:.4f}% 🎉"
            else:
                radar_data["msg"] = f"🔍 فحص مستمر... العائد الحالي: {net_profit:.4f}% (لا توجد فجوة مربحة)"
                
        except Exception as e:
            radar_data["msg"] = f"⚠️ خطأ في الاتصال بالمفاتيح: {str(e)}"

        # واجهة HTML نظيفة باللون الأسود تحدث نفسها قسرياً كل ثانيتين
        html = f"""
        <html>
            <head>
                <meta http-equiv="refresh" content="2">
                <title>HFT V2 - Tornado Live</title>
                <style>
                    body {{ font-family: monospace; background: #0c0c0c; color: #00ff00; padding: 30px; text-align: center; }}
                    .box {{ border: 2px solid #333; padding: 25px; display: inline-block; background: #111; border-radius: 8px; text-align: left; min-width: 350px; }}
                    h2 {{ color: #ffcc00; text-align: center; margin-top:0; }}
                    .val {{ color: #00ffff; font-weight: bold; }}
                </style>
            </head>
            <body>
                <div class="box">
                    <h2>🚀 محرك HFT V2 - رادار مستقل</h2>
                    <p><b>حالة النظام:</b> 📡 متصل ويعمل عبر خادم إنتاجي صلب!</p>
                    <hr style="border-color:#222;">
                    <p>💰 سعر BTCUSDT: <span class="val">{radar_data['btc']} USDT</span></p>
                    <p>💰 سعر DOTBTC: <span class="val">{radar_data['dot_btc']} BTC</span></p>
                    <p>💰 سعر DOTUSDT: <span class="val">{radar_data['dot_usdt']} USDT</span></p>
                    <hr style="border-color:#222;">
                    <p>🎯 <b>النتيجة الحالية:</b> {radar_data['msg']}</p>
                </div>
            </body>
        </html>
        """
        self.write(html)

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    port = int(os.environ.get("PORT", 10000))
    app.listen(port)
    print(f"⚙️ السيرفر الإنتاجي يعمل بنجاح على المنفذ: {port}")
    tornado.ioloop.IOLoop.current().start()
