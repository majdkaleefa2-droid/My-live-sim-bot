import asyncio
import os
import ccxt.pro as ccxtpro
from datetime import datetime

# إعداد الاتصال فائق السرعة بمنصة Gate.io
exchange = ccxtpro.gate({
    'enableRateLimit': True,
    'options': {
        'defaultType': 'spot',
        'ws': {
            'options': {
                'concurrency': 50 # رفع حد المعالجة المتزامنة لقنوات البث
            }
        }
    }
})

# نموذج التكلفة الصارم لحسابات VIP (عمولة منخفضة جداً للاستفادة القصوى)
FEE_PER_LEG = 0.0006  # 0.06% لكل عملية
TOTAL_FEE_3_LEGS = FEE_PER_LEG * 3

# رصيد المحاكاة الافتراضي لبدء صفقات الورق (Paper Trading)
balance_usdt = 1000.0

# 1. قائمة الـ 15 عملة الساخنة البديلة والميم الأكثر تقلباً وحركة
HOT_ALTCOINS = [
    'SOL', 'XRP', 'DOGE', 'ADA', 'AVAX', 
    'LINK', 'DOT', 'SHIB', 'NEAR', 'PEPE', 
    'FET', 'SUI', 'APT', 'WIF', 'BONK'
]

# 2. بناء ذاكرة الكاش اللحظية في الRAM لجميع أطراف المثلثات
orderbook_cache = {}

# تأمين الزوج الحاكم أولاً
orderbook_cache['BTC/USDT'] = {'ask': None, 'bid': None}

# توليد المثلثات تلقائياً للعملات الـ 15
for coin in HOT_ALTCOINS:
    orderbook_cache[f'{coin}/USDT'] = {'ask': None, 'bid': None}
    orderbook_cache[f'{coin}/BTC']  = {'ask': None, 'bid': None}

def process_triangular_arbitrage(coin):
    """
    محرك الحساب والاقتناص اللحظي الخارق (Tick-Driven Micro Engine)
    يعمل في جزء من الألف من الثانية فور ورود السعر
    """
    global balance_usdt
    
    try:
        # أسماء الأزواج للمثلث الحالي
        pair_usdt = f'{coin}/USDT'
        pair_btc  = f'{coin}/BTC'
        pair_base = 'BTC/USDT'
        
        # التأكد من توفر أسعار حية ومحدثة للمثلث بالكامل
        p_base_ask = orderbook_cache[pair_base]['ask']
        p_coin_btc_bid = orderbook_cache[pair_btc]['bid']
        p_coin_usdt_bid = orderbook_cache[pair_usdt]['bid']
        
        if not (p_base_ask and p_coin_btc_bid and p_coin_usdt_bid):
            return # إذا نقص سعر واحد يتخطى المحرك العملية فوراً للحفاظ على السرعة

        # المسار الرياضي الصارم: USDT -> BTC -> COIN -> USDT
        # 1. شراء BTC بواسطة USDT (1 / p_base_ask)
        # 2. شراء العملة الساخنة بواسطة BTC (مقلوب سعر الـ bid للزوج coin/BTC)
        # 3. بيع العملة الساخنة واسترداد USDT (الضرب في سعر bid للزوج coin/USDT)
        raw_return = (1 / p_base_ask) / p_coin_btc_bid * p_coin_usdt_bid
        
        # صافي العائد بعد خصم رسوم الـ 3 صفقات المركبة
        net_return = raw_return - TOTAL_FEE_3_LEGS
        
        # عتبة الربح المستهدفة (0.02% ربح صافي فأكثر)
        if net_return > 1.0002:
            profit_percentage = (net_return - 1) * 100
            gained = balance_usdt * (net_return - 1)
            balance_usdt += gained
            
            timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
            print(f"\n🚨 [اقتناص خارق || {timestamp}]")
            print(f"   المثلث الناجح: USDT ➔ BTC ➔ {coin} ➔ USDT")
            print(f"   العائد الصافي: {net_return:.5f} (+{profit_percentage:.4f}%)")
            print(f"   💰 الرصيد الحالي بالمحاكاة: ${balance_usdt:.2f}\n", flush=True)
            
    except Exception as e:
        pass # تجاهل الأخطاء الطفيفة أثناء العمليات الرياضية السريعة لضمان عدم توقف البوت

async def watch_ticker_stream(symbol):
    """
    مستقبل البيانات الحي الخارق - يغذي الذاكرة ويطلق المحرك دون أي تأخير
    """
    while True:
        try:
            ticker = await exchange.watch_ticker(symbol)
            if ticker and 'ask' in ticker and 'bid' in ticker:
                orderbook_cache[symbol]['ask'] = ticker['ask']
                orderbook_cache[symbol]['bid'] = ticker['bid']
                
                # إذا كان التحديث للزوج الحاكم، نفحص كل العملات
                if symbol == 'BTC/USDT':
                    for coin in HOT_ALTCOINS:
                        process_triangular_arbitrage(coin)
                else:
                    # إذا كان التحديث لعملة معينة، نفحص مثلثها هي فقط توفيراً للوقت والجهد
                    coin_name = symbol.split('/')[0]
                    process_triangular_arbitrage(coin_name)
                    
        except Exception as e:
            await asyncio.sleep(1) # إعادة اتصال سريعة عند حدوث مشاكل في الشبكة

async def main():
    print("⚡ إطلاق محرك البلاك بوكس الخارق (HFT Simulator - 15 Hot Coins) ⚡")
    print("البوت الآن يقوم بفتح 45 قناة اتصال متزامنة ومجانية بالكامل لمراقبة واقتناص الفرص...")
    
    # بناء مصفوفة المهام المتوازية لقنوات الـ WebSocket
    tasks = [watch_ticker_stream('BTC/USDT')]
    
    for coin in HOT_ALTCOINS:
        tasks.append(watch_ticker_stream(f'{coin}/USDT'))
        tasks.append(watch_ticker_stream(f'{coin}/BTC'))
        
    try:
        # تشغيل جميع القنوات والمحركات بالتوازي المطلق
        await asyncio.gather(*tasks)
    except Exception as e:
        print(f"❌ خطأ غير متوقع في المحرك الرئيسي: {e}")
    finally:
        await exchange.close()

if __name__ == '__main__':
    asyncio.run(main())
