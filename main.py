import os
import time
import ccxt

def initialize_bot():
    print("... جاري تهيئة البوت والاتصال بحساب Bybit Demo المدمج (Mainnet V5)")
    
    # 1. جلب المفاتيح من إعدادات Render
    api_key = os.environ.get('BYBIT_API_KEY')
    api_secret = os.environ.get('BYBIT_API_SECRET')
    
    if not api_key or not api_secret:
        print("خطأ: لم يتم العثور على مفاتيح API في إعدادات Render.")
        return None

    # 2. إجبار المكتبة على توجيه الاتصال مباشرة لخوادم الديمو
    # بدون استخدام set_sandbox_mode لتجنب تحويل الرابط إلى testnet.bybit.com
    exchange = ccxt.bybit({
        'apiKey': api_key,
        'secret': api_secret,
        'urls': {
            'api': {
                'public': 'https://api-demo.bybit.com',
                'private': 'https://api-demo.bybit.com',
            }
        },
        'options': {
            'enableDemoTrading': True,  # التفعيل البرمجي المباشر للديمو
            'defaultType': 'swap',      # تداول العقود الآجلة
        }
    })

    try:
        # فحص الاتصال وقراءة رصيد حساب الديمو الفعلي
        balance = exchange.fetch_balance()
        print("🎉 تم الاتصال والربط بنجاح كامل مع حساب Bybit Demo!")
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
    symbols = ['BTC/USDT:USDT', 'NEAR/USDT:USDT']
    
    while True:
        try:
            for symbol in symbols:
                ticker = exchange.fetch_ticker(symbol)
                print(f"🔹 سعر Bybit اللحظي لـ {symbol}: {ticker['last']}")
                
            time.sleep(1) 
            
        except Exception as e:
            print(f"⚠️ تنبيه: حدث خطأ مؤقت أثناء قراءة الأسعار: {e}")
            time.sleep(5)

if __name__ == "__main__":
    exchange_client = initialize_bot()
    if exchange_client:
        start_trading_loop(exchange_client)
