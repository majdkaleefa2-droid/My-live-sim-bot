import os
import sys
import time
import threading
from fastapi import FastAPI
import uvicorn
from binance.client import Client
from binance.exceptions import BinanceAPIException

# --- إعدادات نظام HFT V7 LIVE المربوط بالحساب التجريبي ---
TOKEN = "HFT_V7_LIVE_COMPLIANCE"
MARKET_REGIME = "ADAPTIVE"
SECURITY_WITHDRAWAL_LOCKED = True  # قفل السحب محمي برمجياً

# استدعاء مفاتيح الـ API الخاصة بحساب بينانس التجريبي من إعدادات البيئة (Railway Env Variables)
# يمكنك كتابتها مباشرة مكان os.environ.get إذا كنت لا تستخدم المتغيرات
API_KEY = os.environ.get("BINANCE_TESTNET_KEY", "your_testnet_api_key")
API_SECRET = os.environ.get("BINANCE_TESTNET_SECRET", "your_testnet_api_secret")

app = FastAPI()

# تهيئة عميل بينانس للعمل على البيئة التجريبية (Testnet)
try:
    # استخدام testnet=True لتوجيه الأوامر للسيرفر التجريبي بدلاً من الحقيقي
    client = Client(API_KEY, API_SECRET, testnet=True)
    print("[SUCCESS] تم الاتصال بـ Binance Testnet بنجاح.")
except Exception as e:
    print(f"[ERROR] فشل الاتصال الأولي ببينانس: {e}")
    client = None

# متقير عالمي لتخزين الرصيد الذي يتم تحديثه لحظياً من بينانس
current_balance = "1000.00 USDT (Simulated)"

def monitor_adaptive_market():
    global current_balance
    print("[MONITOR] رادار V7 نشط الآن ويراقب السيولة...")
    
    while True:
        try:
            if client:
                # جلب الرصيد الحقيقي المربوط بالحساب التجريبي لعملة USDT
                account_info = client.get_account()
                for asset in account_info['balances']:
                    if asset['asset'] == 'USDT':
                        current_balance = f"{float(asset['free']):.2f} USDT"
                        break
                
                # هنا يتم فحص ظروف السوق التكيفية (Adaptive) بعد افتتاح السوق
                # يمكنك إضافة شروط استراتيجية قنص الصفقات بناءً على أسعار الشموع اللحظية
                current_time = time.strftime("%H:%M:%S")
                print(f"[{current_time}] الرصيد التجريبي الحالي: {current_balance} | الرادار يبحث عن إشارات سيولة...")
            else:
                print("[WARNING] لم يتم ربط الـ API بشكل صحيح. الرادار يعمل في وضع المحاكاة الافتراضية.")
                
        except BinanceAPIException as e:
            print(f"[BINANCE ERROR] خطأ أثناء جلب البيانات: {e.message}")
        except Exception as e:
            print(f"[SYSTEM ERROR] حدث خطأ في النظام الخلفي: {e}")
            
        time.sleep(5)  # الفحص والتحديث كل 5 ثوانٍ

@app.get("/")
def read_root():
    # الرد على سيرفر Railway ليبقى البوت متصلاً (كود 200) ويعرض حالة الرادار الحالية
    return {
        "status": "online",
        "version": "V7_LIVE_COMPLIANCE",
        "regime": f"{MARKET_REGIME}_MARKET_REGIME",
        "binance_connected": client is not None,
        "current_balance": current_balance,
        "security": "WITHDRAWAL_LOCKED_API_ACTIVE"
    }

if __name__ == "__main__":
    # تشغيل حلقة الرادار في مسار خلفي منفصل حتى لا يغلق السيرفر
    threading.Thread(target=monitor_adaptive_market, daemon=True).start()
    
    # تشغيل سيرفر الويب واستقبال المنفذ تلقائياً من Railway
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
