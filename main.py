import asyncio
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import ccxt

app = FastAPI(title="HFT V7 Pulse Rider - PRO SHIELD")

# 1. الإعدادات المتطورة وصمامات الأمان الصارمة
BotConfig = {
    "bot_name": "HFT_V7_PULSE_RIDER_PRO_SHIELD",
    "version": "7.0.0",
    "environment": "binance-testnet-simulation",
    "symbol": "BTC/USDT",  # العملة المراد مراقبتها
    "baseCapital": 200.00,  # محفظة افتراضية بالـ USDT
    "riskManagement": {
        "drawdownProtection": True,
        "maxDrawdownPercent": 5.0,  # صمام التراجع 5%
        "stopLossLimit": 10.0      # أقصى خسارة 10 USDT
    }
}

# 2. إعداد الاتصال الآمن بمنصة بينانس التجريبية (Testnet)
# ملاحظة: يمكنك تشغيل الكود لجلب الأسعار حتى بدون إدخال المفاتيح، ولكن لإرسال أوامر وهمية ستحتاج لمفاتيح Testnet من موقع بينانس
exchange = ccxt.binance({
    'apiKey': 'YOUR_TESTNET_API_KEY',     # ضع مفتاح التيست نت هنا
    'secret': 'YOUR_TESTNET_SECRET_KEY',   # ضع السكرت الخاص بالتيست نت هنا
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future',  # لتجربة العقود الآجلة أو 'spot' للتداول الفوري
    }
})

# تفعيل وضع الحساب التجريبي الوهمي إجبارياً لحمايتك
exchange.set_sandbox_mode(True)

# 3. دالة جلب بيانات السوق الحية
async def get_live_market_data(symbol: str):
    try:
        # جلب السعر اللحظي من بينانس
        ticker = exchange.fetch_ticker(symbol)
        return {
            "status": "connected",
            "symbol": symbol,
            "live_price": ticker['last'],
            "high": ticker['high'],
            "low": ticker['low'],
            "volume": ticker['quoteVolume']
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"فشل الاتصال ببينانس: {str(e)}"
        }

# 4. واجهة التحكم الرسومية عبر المتصفح (Dashboard)
@app.get("/", response_class=HTMLResponse)
async def dashboard():
    # جلب البيانات الحية قبل عرض الصفحة
    market = await get_live_market_data(BotConfig["symbol"])
    
    # حساب صمامات الأمان بناءً على السعر الحالي والمخاطرة
    max_loss_allowed = BotConfig["baseCapital"] * (BotConfig["riskManagement"]["maxDrawdownPercent"] / 100)
    
    html_content = f"""
    <html>
        <head>
            <title>{BotConfig["bot_name"]}</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #121212; color: #ffffff; padding: 20px; }}
                .container {{ max-width: 800px; margin: auto; background: #1e1e1e; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.5); }}
                h1 {{ color: #f3ba2f; border-bottom: 2px solid #333; padding-bottom: 10px; }}
                .status {{ font-weight: bold; color: #00ff00; }}
                .error {{ font-weight: bold; color: #ff0000; }}
                .metric-box {{ display: flex; justify-content: space-between; background: #2a2a2a; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                .shield-active {{ border-left: 5px solid #f3ba2f; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🛡️ {BotConfig["bot_name"]} - إصدار V7 PRO SHIELD</h1>
                <p><strong>حالة النظام:</strong> <span class="status">يعمل محلياً بأمان (Sandbox Mode)</span></p>
                <p><strong>البيئة الحالية:</strong> {BotConfig["environment"]}</p>
                
                <h2>📊 بيانات السوق الحية (منصة Binance)</h2>
                <div class="metric-box">
                    <span>الزوج المراقب:</span>
                    <strong>{BotConfig["symbol"]}</strong>
                </div>
                <div class="metric-box">
                    <span>السعر الحالي المباشر:</span>
                    <strong style="color: #f3ba2f;">${market.get('live_price', 'غير قادر على الجلب')}</strong>
                </div>
                
                <h2>🛡️ إعدادات صمام الأمان (Risk Management)</h2>
                <div class="metric-box shield-active">
                    <span>رأس المال الافتراضي:</span>
                    <span>{BotConfig["baseCapital"]} USDT</span>
                </div>
                <div class="metric-box shield-active">
                    <span>حد التراجع الأقصى المسموح (Drawdown):</span>
                    <span>{BotConfig["riskManagement"]["maxDrawdownPercent"]}% ({max_loss_allowed} USDT)</span>
                </div>
                <div class="metric-box shield-active">
                    <span>حد وقف الخسارة الإجمالي (Stop Loss):</span>
                    <span>{BotConfig["riskManagement"]["stopLossLimit"]} USDT</span>
                </div>
            </div>
        </body>
    </html>
    """
    return html_content

# 5. تشغيل السيرفر المحلي تلقائياً عند تشغيل الملف
if __name__ == "__main__":
    import uvicorn
    # تشغيل السيرفر المحلي على الرابط http://127.0.0.1:8000
    uvicorn.run(app, host="127.0.0.1", port=8000)
