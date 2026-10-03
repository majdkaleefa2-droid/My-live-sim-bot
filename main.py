import os
import asyncio
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer
from binance import AsyncClient, BinanceSocketManager

# 1. جلب المفاتيح بشكل آمن من بيئة عمل Render المجانية
API_KEY = os.getenv('BINANCE_API_KEY')
SECRET_KEY = os.getenv('BINANCE_SECRET_KEY')

if not API_KEY or not SECRET_KEY:
    raise ValueError("خطأ: لم يتم العثور على مفاتيح Binance في إعدادات Render!")

# قائمة الـ 15 عملة الساخنة (Hot Coins) للمضاربة الخاطفة
HOT_SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT",
    "ADAUSDT", "AVAXUSDT", "DOTUSDT", "LINKUSDT", "MATICUSDT",
    "DOGEUSDT", "SHIBUSDT", "TRXUSDT", "LTCUSDT", "NEARUSDT"
]

streams = [f"{symbol.lower()}@ticker" for symbol in HOT_SYMBOLS]


# --- 🛠️ الجزء الخاص بالحفاظ على استمرارية الخطة المجانية في Render ---
def run_dummy_server():
    """خادم وهمي لإيهام Render أن التطبيق نشط لمنع إيقافه تلقائياً"""
    port = int(os.getenv("PORT", 10000))  # جلب المنفذ الذي تفرضه Render
    server_address = ('', port)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print(f"📡 تم تشغيل خادم الحفاظ على بيئة الاستضافة المجانية على منفذ: {port}")
    httpd.serve_forever()


async def process_signal(symbol, current_price, client):
    """
    🔥 هنا قلب إستراتيجية المضاربة بأجزاء الثانية الحية.
    البيانات تتدفق هنا بسرعة فائقة بشكل متوازٍ وغير متزامن.
    """
    # حالياً نقوم بطباعة الأسعار الحية في الـ Logs للتأكد من نجاح الربط
    print(f"⚡ [تحديث لحظي] العملة: {symbol} | السعر الحالي: {current_price} USDT")
    
    # هنا سنحقن شروط البيع والشراء بناءً على قرارك القادم


async def main():
    print("🚀 بدء تشغيل بوت المضاربة الخاطفة غير المتزامن على الخطة المجانية لـ Render...")
    print(f"👀 مراقبة {len(HOT_SYMBOLS)} عملة ساخنة بأجزاء الثانية عبر الـ WebSockets.")

    # إنشاء العميل غير المتزامن وتوجيهه لشبكة الاختبار التجريبية (Testnet)
    client = await AsyncClient.create(API_KEY, SECRET_KEY, testnet=True)
    bm = BinanceSocketManager(client)
    
    # فتح خط بث مباشر مشترك (Multiplex) لمنع حظر الـ IP
    multiplex_socket = bm.multiplex_socket(streams)

    async with multiplex_socket as stream:
        while True:
            try:
                res = await stream.recv()
                if res and 'data' in res:
                    data = res['data']
                    symbol = data['s']        # اسم العملة
                    current_price = data['c'] # السعر اللحظي الحالي
                    
                    # تمرير البيانات فوراً وبشكل موازي لمعالجة صفقات المضاربة
                    asyncio.create_task(process_signal(symbol, current_price, client))
                    
            except Exception as e:
                print(f"⚠️ خطأ في استقبال بيانات البث المباشر: {e}")
                await asyncio.sleep(5)
                
    await client.close_connection()

if __name__ == "__main__":
    # 1. تشغيل الخادم الوهمي في خيط منفصل (Thread) ليرضي نظام Render المجاني
    server_thread = threading.Thread(target=run_dummy_server, daemon=True)
    server_thread.start()

    # 2. تشغيل الحلقة اللانهائية الأساسية للبوت
    asyncio.run(main())
