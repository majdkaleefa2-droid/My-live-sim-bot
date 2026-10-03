import os
import asyncio
from binance import AsyncClient, BinanceSocketManager
from binance.exceptions import BinanceAPIException

# 1. جلب المفاتيح بشكل آمن من بيئة عمل Render
API_KEY = os.getenv('BINANCE_API_KEY')
SECRET_KEY = os.getenv('BINANCE_SECRET_KEY')

if not API_KEY or not SECRET_KEY:
    raise ValueError("خطأ: لم يتم العثور على مفاتيح Binance في إعدادات Render!")

# 2. قائمة الـ 15 عملة الساخنة (Hot Coins) مقابل الـ USDT التي اتفقنا على المضاربة عليها
# يمكنك تعديل أو استبدال أي عملة في القائمة حسب تحديثات السوق الحالية
HOT_SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT",
    "ADAUSDT", "AVAXUSDT", "DOTUSDT", "LINKUSDT", "MATICUSDT",
    "DOGEUSDT", "SHIBUSDT", "TRXUSDT", "LTCUSDT", "NEARUSDT"
]

# تحويل أسماء العملات إلى أحرف صغيرة توافقاً مع شروط الـ WebSocket لبينانس
streams = [f"{symbol.lower()}@ticker" for symbol in HOT_SYMBOLS]


async def process_signal(symbol, current_price, client):
    """
    هنا قلب الإستراتيجية والمضاربة بأجزاء الثانية.
    بما أن الدالة تعمل بنظام Async، فسيتم فحص واتخاذ القرار لكل عملة بشكل منفصل وموازي.
    """
    # 💡 مثال إستراتيجيتنا السريعة: (ضع هنا شروط الدخول والخروج الخاصة بك)
    # سنقوم هنا فقط بطباعة السعر اللحظي المتدفق بأجزاء الثانية للتأكد من عمل البوت
    print(f"⚡ [تحديث لحظي] العملة: {symbol} | السعر الحالي: {current_price} USDT")
    
    # مثال على إرسال أمر شراء غير متزامن سريع إذا تحقق شرطك:
    # try:
    #     order = await client.create_order(
    #         symbol=symbol,
    #         side='BUY',
    #         type='MARKET',
    #         quantity=0.001  # احرص على حساب الكمية المناسبة لكل عملة
    #     )
    #     print(f"✅ تم تنفيذ أمر شراء سريع لـ {symbol}")
    # except BinanceAPIException as e:
    #     print(f"❌ فشل تنفيذ الأمر لـ {symbol}: {e.message}")


async def main():
    print("🚀 بدء تشغيل بوت المضاربة الخاطفة غير المتزامن على Render...")
    print(f"👀 مراقبة {len(HOT_SYMBOLS)} عملة ساخنة بأجزاء الثانية عبر الـ WebSockets.")

    # إنشاء العميل غير المتزامن وتوجيهه لشبكة الاختبار (Testnet)
    client = await AsyncClient.create(API_KEY, SECRET_KEY, testnet=True)
    bm = BinanceSocketManager(client)
    
    # فتح خط بث مباشر متعدد (Multiplex Socket) لمراقبة الـ 15 عملة معاً في نفس خط الاتصال
    # هذا يمنع تماماً حظر الـ IP لأنه يستهلك طلب واحد فقط بدلاً من آلاف الطلبات
    multiplex_socket = bm.multiplex_socket(streams)

    async with multiplex_socket as stream:
        while True:
            try:
                # استقبال البيانات المتدفقة بأجزاء الثانية من بينانس
                res = await stream.recv()
                
                if res and 'data' in res:
                    data = res['data']
                    symbol = data['s']        # اسم العملة (مثل BTCUSDT)
                    current_price = data['c'] # السعر الحالي والإغلاق اللحظي
                    
                    # تمرير البيانات فوراً وبشكل موازي لمعالجتها واتخاذ قرار المضاربة
                    asyncio.create_task(process_signal(symbol, current_price, client))
                    
            except Exception as e:
                print(f"⚠️ خطأ أثناء استقبال بيانات البث: {e}")
                print("إعادة الاتصال بالبث المباشر خلال 5 ثوانٍ...")
                await asyncio.sleep(5)
                
    # إغلاق الاتصال بأمان عند إيقاف البوت
    await client.close_connection()

if __name__ == "__main__":
    # تشغيل الحلقة اللانهائية غير المتزامنة لضمان استقرار البوت على خوادم Render
    asyncio.run(main())
