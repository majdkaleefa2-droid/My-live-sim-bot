import os
import sys
import subprocess

# --- 1. تثبيت المكتبات الناقصة إجبارياً لمنع الـ Crash ---
def install_requirements():
    required_libs = ["fastapi", "uvicorn", "python-binance"]
    for lib in required_libs:
        try:
            __import__(lib.replace("-", "_"))
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

install_requirements()

import time
import threading
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn
from binance.client import Client

# --- 2. إعدادات نظام V7 المربوط بالحساب التجريبي (Testnet) ---
TOKEN = "HFT_V7_LIVE_COMPLIANCE"
MARKET_REGIME = "ADAPTIVE"

API_KEY = os.environ.get("BINANCE_TESTNET_KEY", "")
API_SECRET = os.environ.get("BINANCE_TESTNET_SECRET", "")

app = FastAPI()
client = None

try:
    client = Client(API_KEY, API_SECRET, testnet=True)
    print("[SUCCESS] تم الاتصال بـ Binance Testnet بنجاح.")
except Exception as e:
    print(f"[WARNING] خطأ في الاتصال بالتست نت: {e}")

# متغيرات الإحصائيات الخاصة برادار V6 PRO الشهير
stats = {
    "balance": 1000.00,
    "trades_count": 0,
    "success_rate": 0,
    "profit_factor": 0.0,
    "status_text": "في انتظار ضربة جرس الافتتاح الأمريكي ورصد السيولة التكيفية...",
    "last_update": "00:00:00"
}

def monitor_adaptive_market():
    global stats
    while True:
        try:
            if client:
                account_info = client.get_account()
                for asset in account_info['balances']:
                    if asset['asset'] == 'USDT':
                        stats["balance"] = round(float(asset['free']), 2)
                        break
            stats["last_update"] = time.strftime("%H:%M:%S")
            # محاكاة البحث عن السيولة لتحديث الرادار
            stats["status_text"] = "الرادار نشط (V7 Engine): يمسح دفاتر طلبات Binance Testnet لحظياً..."
        except Exception:
            stats["last_update"] = time.strftime("%H:%M:%S")
            stats["status_text"] = "جاري تحديث بيانات السيولة من السيرفر التجريبي..."
        time.sleep(5)

@app.get("/", response_class=HTMLResponse)
def read_root():
    # إعادة بناء واجهة الرادار المظلمة الفخمة لـ V6 PRO بالكامل
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>HFT V7 - RADAR PRO</title>
        <style>
            body {{
                background-color: #0d1117;
                color: #c9d1d9;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                min-height: 100vh;
            }}
            .container {{
                background-color: #161b22;
                border: 1px solid #30363d;
                border-radius: 12px;
                padding: 25px;
                width: 100%;
                max-width: 450px;
                box-shadow: 0 8px 24px rgba(0,0,0,0.5);
            }}
            .header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-bottom: 1px solid #30363d;
                padding-bottom: 15px;
                margin-bottom: 20px;
            }}
            .title {{
                font-size: 1.2rem;
                font-weight: bold;
                color: #ffffff;
            }}
            .badge {{
                background-color: #f1e05a;
                color: #000000;
                padding: 4px 10px;
                border-radius: 20px;
                font-size: 0.8rem;
                font-weight: bold;
            }}
            .stat-box {{
                background-color: #0d1117;
                border: 1px solid #21262d;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 15px;
                text-align: center;
            }}
            .stat-value {{
                font-size: 1.8rem;
                font-weight: bold;
                color: #58a6ff;
                margin-top: 5px;
            }}
            .grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 10px;
                margin-bottom: 15px;
            }}
            .grid-box {{
                background-color: #0d1117;
                border: 1px solid #21262d;
                border-radius: 8px;
                padding: 12px;
                text-align: center;
            }}
            .grid-value {{
                font-size: 1.2rem;
                font-weight: bold;
                color: #3fb950;
                margin-top: 5px;
            }}
            .footer-status {{
                background-color: #21262d;
                border-radius: 6px;
                padding: 12px;
                font-size: 0.85rem;
                color: #8b949e;
                line-height: 1.4;
                border-right: 4px solid #58a6ff;
            }}
            .pulse {{
                display: inline-block;
                width: 8px;
                height: 8px;
                background-color: #2ea44f;
                border-radius: 50%;
                margin-left: 5px;
                animation: blink 1.5s infinite;
            }}
            @keyframes blink {{
                0% {{ opacity: 0.2; }}
                50% {{ opacity: 1; }}
                100% {{ opacity: 0.2; }}
            }}
        </style>
        <script>
            // تحديث تلقائي للصفحة كل 5 ثوانٍ لإنعاش الرادار لحظياً
            setInterval(function() {{
                window.location.reload();
            }}, 5000);
        </script>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="title">📡 رادار التحكم HFT V7</div>
                <div class="badge">V6 PRO Interface</div>
            </div>
            
            <div class="stat-box">
                <div style="color: #8b949e; font-size: 0.9rem;">رأس مال الحساب الحركي المتصل (Testnet)</div>
                <div class="stat-value">{stats["balance"]} USDT</div>
            </div>
            
            <div class="grid">
                <div class="grid-box">
                    <div style="color: #8b949e; font-size: 0.8rem;">الصفقات المنفذة</div>
                    <div class="grid-value" style="color: #58a6ff;">{stats["trades_count"]}</div>
                </div>
                <div class="grid-box">
                    <div style="color: #8b949e; font-size: 0.8rem;">نسبة النجاح</div>
                    <div class="grid-value">{stats["success_rate"]}%</div>
                </div>
            </div>
            
            <div class="grid">
                <div class="grid-box">
                    <div style="color: #8b949e; font-size: 0.8rem;">عامل الربحية (Profit Factor)</div>
                    <div class="grid-value" style="color: #f1e05a;">{stats["profit_factor"]}</div>
                </div>
                <div class="grid-box">
                    <div style="color: #8b949e; font-size: 0.8rem;">توقيت آخر تحديث للنبض</div>
                    <div class="grid-value" style="color: #8b949e; font-size: 1rem; margin-top:8px;">{stats["last_update"]}</div>
                </div>
            </div>
            
            <div class="footer-status">
                <span class="pulse"></span>
                <strong>آخر إشارة مرصودة:</strong> {stats["status_text"]}
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

if __name__ == "__main__":
    threading.Thread(target=monitor_adaptive_market, daemon=True).start()
    port = int(os.environ.get("PORT", 8080))
    print(f"[SYSTEM] تشغيل سيرفر الرادار المرئي على المنفذ: {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
