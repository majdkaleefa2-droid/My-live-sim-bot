import os
import time
import ccxt

def initialize_bot():
    print("جاري تهيئة البوت والاتصال بمنصة Bybit التجريبية...")
    
    # 1. جلب المفاتيح من إعدادات البيئة في Render التي قمنا بضبطها معاً
    api_key = os.environ.get('BYBIT_API_KEY')
    api_secret = os.environ.get('BYBIT_API_SECRET')
    
    if not api_key or not api_secret:
        print("خطأ: لم يتم العثور على مفاتيح API في إعدادات Render. يرجى التحقق من المفاتيح.")
        return None

    # 2. تعريف كائن المنصة باستخدام مكتبة CCXT
    exchange = ccxt.bybit({
        'apiKey': api_key,
        'secret': api_secret,
        'options': {
            'defaultType': 'swap',  # لتوجيه البوت تلقائياً إلى العقود الآجلة المستمرة
        }
    })

    # 3. السطر السحري الجديد لتشغيل التداول التجريبي المدمج (Demo Trading)
    # هذا البديل الصحيح لـ set_sandbox_mode لتصل الصفقات للحساب الحالي
    exchange.set_sandbox_mode(True) 
    
    # بعض إصدارات ccxt تحتاج التفعيل المباشر أيضاً عبر الخيارات
    exchange.options['enableDemoTrading'] = True

    try:
        # فحص الاتصال وقراءة الرصيد للتأكد من نجاح الربط
        balance = exchange.fetch_balance()
        print("تم الاتصال بنجاح كامل! رصيدك التجريبي المتاح هو:")
        print(balance['total'])
        return exchange
    except Exception as e:
        print(f"فشل الاتصال بالمنصة. السبب التقني للخطأ هو: {e}")
        return None

def start_trading_loop(exchange):
    if not exchange:
        return
        
    print("بدء حلقة التداول اللحظي (HFT)...")
    
    # استبدل هذا الجزء بمنطق استراتيجيتك البرمجية الخاصة (شراء/بيع)
    # هذا مجرد هيكل تشغيلي حقيقي يقرأ الأسعار حية
    symbols = ['BTC/USDT:USDT', 'NEAR/USDT:USDT']
    
    while True:
        try:
            for symbol in symbols:
                ticker = exchange.fetch_ticker(symbol)
                print(f"سعر Bybit اللحظي لـ {symbol}: {ticker['last']}")
                
                # هنا يتم وضع دوال الشراء والبيع الخاصة بك (create_order)
                
            # فاصل زمني (1 ثانية) لحماية السيرفر من الحظر وضمان استقرار الاتصال
            time.sleep(1) 
            
        except Exception as e:
            print(f"حدث خطأ أثناء قراءة البيانات: {e}")
            time.sleep(5)

if __name__ == "__main__":
    exchange_client = initialize_bot()
    if exchange_client:
        start_trading_loop(exchange_client)
