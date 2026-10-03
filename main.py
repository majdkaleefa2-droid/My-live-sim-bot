import os
import asyncio
from flask import Flask
from binance import AsyncClient, BinanceSocketManager

# --- 1. إعداد خادم Flask الذكي لإمساك المنفذ (Port) بنجاح ---
app = Flask(__name__)

@app.route('/')
def home():
    return "⚡ الرادار الحسابي يعمل بنجاح وبأجزاء الثانية في الخلفية! 🚀"

# --- 2. متغيرات الرادار وإستراتيجية الزخم والـ API ---
API_KEY = os.getenv('BINANCE_API_KEY')
SECRET_KEY = os.getenv('BINANCE_SECRET_KEY')

HOT_SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT",
    "ADAUSDT", "AVAXUSDT", "DOTUSDT", "LINKUSDT", "MATICUSDT",
    "DOGEUSDT", "SHIBUSDT", "TRXUSDT", "LTCUSDT", "NEARUSDT"
]

streams = [f"{symbol.lower()}@ticker" for symbol in HOT_SYMBOLS]

# متغيرات الحسابات الميدانية
TRADE_AMOUNT_USDT = 100.0
TAKE_PROFIT_PCT = 0.01
STOP_LOSS_PCT = 0.005
PUMP_THRESHOLD_PCT = 0.003

last_prices = {}
active_trades = {}

async def process_signal(symbol, current_price, client):
    """
    🔥 قلب الرادار لتتبع صفقات الـ 15 عملة في نفس الملي ثانية
    """
    global last_prices, active_trades
    
    # فحص خروج الصفقة المفتوحة
    if symbol in active_trades:
        entry_price = active_trades[symbol]['entry_price']
        price_change_from_entry = (current_price - entry_price) / entry_price
        
        if price_change_from_entry >= TAKE_PROFIT_PCT:
            print(f"💰 [جني أرباح] {symbol} صعدت! جاري البيع وجني الأرباح...")
            del active_trades[symbol]
        elif price_change_from_entry <= -STOP_LOSS_PCT:
            print(f"🚨 [وقف خسارة] {symbol} عكس الاتجاه! جاري الخروج الفوري...")
            del active_trades[symbol]
        return

    # فحص إشارة دخول جديدة
    if symbol in last_prices:
        prev_price = last_prices[symbol]
        price_change = (current_price - prev_price) / prev_price
        
        if price_change >= PUMP_THRESHOLD_PCT and symbol not in active_trades:
            print(f"⚡ [إشارة رادار] رصد قفزة زخم لـ {symbol} بنسبة {price_change*100:.3f}%")
            try:
                quantity = round(TRADE_AMOUNT_USDT / current_price, 4)
                # تنفيذ الشراء على حساب بينانس التجريبي (Testnet)
                order = await client.create_order(
                    symbol=symbol, side='BUY', type='MARKET', quantity=quantity
                )
                active_trades[symbol] = {
                    'entry_price': current_price,
                    'quantity': quantity,
                    'order_id': order.get('orderId', 0)
                }
                print(f"🛒 نجح الشراء التلقائي لـ {symbol} بسعر: {current_price} USDT")
            except Exception as e:
                print(f"❌ تعذر تنفيذ الصفقة لـ {symbol} في الشبكة التجريبية: {e}")

    last_prices[symbol] = current_price


async def run_binance_radar():
    """تفعيل الرادار بشكل مباشر داخل الـ Event Loop الرئيسي لضمان الاستجابة"""
    print("🚀 جاري بدء تشغيل رادار الـ 15 عملة الساخنة...")
    if not API_KEY or not SECRET_KEY:
        print("❌ خطأ قاطع: لم يتم العثور على مفاتيح Binance!")
        return

    client = await AsyncClient.create(API_KEY, SECRET_KEY, testnet=True)
    bm = BinanceSocketManager(client)
    multiplex_socket = bm.multiplex_socket(streams)

    print("🔗 تم فتح قنوات البث المباشر (WebSockets) للرادار بنجاح!")
    async with multiplex_socket as stream:
        while True:
            try:
                res = await stream.recv()
                if res and 'data' in res:
                    data = res['data']
                    symbol = data['s']
                    current_price = float(data['c'])
                    
                    # طباعة فورية للتأكد من وصول الأسعار أولاً بأول في الـ Logs
                    print(f"📈 [رادار] {symbol}: {current_price} USDT")
                    
                    asyncio.create_task(process_signal(symbol, current_price, client))
            except Exception as e:
                print(f"⚠️ تنبيه البث المباشر: {e}")
                await asyncio.sleep(1)


async def main():
    """الحلقة الأم التي تدمج خادم الويب لـ Render والرادار معاً بشكل متزامن صلب"""
    # 1. تشغيل خادم Flask بشكل موازٍ غير معطل
    port = int(os.environ.get("PORT", 10000))
    
    # تشغيل Flask بأمان داخل خادم العمل غير المتزامن لـ Asyncio
    loop = asyncio.get_event_loop()
    flask_server = json_server = loop.run_in_executor(
        None, lambda: app.run(host="0.0.0.0", port=port, use_reloader=False)
    )
    
    # 2. تشغيل رادار بينانس في نفس اللحظة والملي ثانية
    await run_binance_radar()

if __name__ == "__main__":
    asyncio.run(main())
