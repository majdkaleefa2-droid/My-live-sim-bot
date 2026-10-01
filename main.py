import time
import ccxt

print("⚡ بَدْء تشغيل البوت بمحفظة محلية وهمية وسعر حي من بينانس...")
print("-" * 60)

# الاتصال العام بمنصة بينانس لسحب الأسعار الحية (مجاني ولا يتطلب API)
exchange = ccxt.binance()

# إعدادات المحفظة الوهمية داخل السيرفر
USDT_BALANCE = 1000.0  # رأس مال وهمي للبدء والقياس
TOTAL_FEES = 0.001 * 3 # خصم عمولة بينانس الحقيقية لـ 3 صفقات (0.3% إجمالي)

print(f"💰 رأس المال التجريبي المحفوظ في السيرفر: {USDT_BALANCE:.2f} USDT")
print("-" * 60)

# تشغيل الفحص المستمر للأبد على السيرفر
while True:
    try:
        # سحب الأسعار اللحظية الفورية
        btc_ticker = exchange.fetch_ticker('BTC/USDT')
        eth_ticker = exchange.fetch_ticker('ETH/USDT')
        eth_btc_ticker = exchange.fetch_ticker('ETH/BTC')
        
        btc_ask = btc_ticker['ask']       # سعر الشراء للبيتكوين
        eth_btc_bid = eth_btc_ticker['bid']  # سعر بيع الإيثيريوم مقابل البيتكوين
        eth_bid = eth_ticker['bid']       # سعر بيع الإيثيريوم مقابل الدولار
        
        # حسبة العائد الصافي من الدورة الثلاثية
        raw_return = (1 / btc_ask) / (1 / eth_btc_bid) * eth_bid
        net_return = raw_return * (1 - TOTAL_FEES)
        
        # طباعة الفحص الدوري في سجلات السيرفر
        print(f"🔄 فحص حقيقي | BTC: {btc_ask:.1f} | العائد الصافي: {net_return:.5f}")
        
        # إذا كانت هناك فرصة ربح حقيقية تتجاوز الرسوم في السوق
        if net_return > 1.0001: 
            profit_percent = (net_return - 1) * 100
            old_balance = USDT_BALANCE
            
            # محاكاة التنفيذ وتحديث المحفظة داخلياً
            USDT_BALANCE = USDT_BALANCE * net_return
            profit_amount = USDT_BALANCE - old_balance
            
            print(f"🚨 [اقتناص فرصة ربح حقيقية في السوق!]")
            print(f"📈 نسبة الربح: +{profit_percent:.4f}%")
            print(f"💸 الأرباح المحققة: +{profit_amount:.4f} USDT")
            print(f"💳 الرصيد الجديد في المحفظة: {USDT_BALANCE:.2f} USDT")
            print("-" * 40)
            
    except Exception as e:
        # حماية البوت من التوقف لو حدث بطء مؤقت في الإنترنت
        pass
        
    # الانتظار لمدة 3 ثوانٍ قبل الفحص التالي لتجنب ضغط السيرفر
    time.sleep(3)
