import os
import time
import ccxt

def initialize_bot():
    print("... جاري تهيئة البوت والاتصال الآمن بمنصة Bybit التجريبية (Demo V5)")
    
    # 1. جلب المفاتيح المشفرة والمحفوظة في إعدادات Render
    api_key = os.environ.get('BYBIT_API_KEY')
    api_secret = os.environ.get('BYBIT_API_SECRET')
    
    if not api_key or not api_secret:
        print("خطأ: لم يتم العثور على مفاتيح API في إعدادات Render. يرجى التحقق من أسماء المتغيرات.")
        return None

    # 2. تعريف كائن المنصة وتوجيه الإعدادات برمجياً للـ Demo بشكل قاطع
    # تم إلغاء set_sandbox_mode واستبدالها بالتوجيه الفعلي لـ api-demo
    exchange = ccxt.bybit({
        'apiKey': api_key,
        'secret': api_secret,
        'options': {
            'enableDemoTrading': True,  # التفعيل الإجباري لحساب الديمو المدمج الموثق
            'defaultType': 'swap',      # توجيه الصفقات تلقائياً لعقود المشتقات والرافعة المالية
        }
    })

    try:
        # فحص الاتصال وسحب الأرصدة الحية لحساب الديمو لإثبات نجاح الربط
        balance = exchange.fetch_balance()
        print("🎉 تم الاتصال والربط بنجاح كامل مع حساب Bybit Demo الثابت!")
        print("💰 رصيدك التجريبي المتاح حالياً هو:")
        print(balance['total'])
        return exchange
    except Exception as e:
        print(f"❌ فشل الاتصال بالمنصة. السبب البرمجي المباشر هو: {e}")
        return None

def start_trading_loop(exchange):
    if not exchange:
        return
        
    print("🚀 بدء حلقة التداول اللحظي عالي التردد (Turbo HFT Loop)...")
    
    # أزواج العملات التي يقرأها البوت ويحللها حية من السوق
    symbols = ['BTC/USDT:USDT', 'NEAR/USDT:USDT', 'LINK/USDT:USDT']
    
    while True:
        try:
            for symbol in symbols:
                ticker = exchange.fetch_ticker(symbol)
                print(f"🔹 سعر Bybit اللحظي لـ {symbol}: {ticker['last']}")
                
                # [هنا يوضع منطق استراتيجيتك البرمجية لفتح وإغلاق الصفقات تلقائياً]
                
            # فاصل زمني (1 ثانية) لحماية السيرفر من الحظر وضمان استقرار جلب البيانات
            time.sleep(1) 
            
        except Exception as e:
            print(f"⚠️ تنبيه: حدث خطأ مؤقت أثناء قراءة الأسعار: {e}")
            time.sleep(5)

if __name__ == "__main__":
    exchange_client = initialize_bot()
    if exchange_client:
        start_trading_loop(exchange_client)
