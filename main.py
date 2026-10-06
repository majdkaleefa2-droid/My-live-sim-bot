import asyncio
import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from binance import AsyncClient
import uvicorn

app = FastAPI()

API_KEY = os.environ.get("BINANCE_API_KEY", "")
SECRET_KEY = os.environ.get("BINANCE_SECRET_KEY", "")

BotConfig = {
    "bot_name": "HFT_V7_PULSE_RIDER_PRO_SHIELD",
    "version": "7.7.0",
    "environment": "binance-spot-testnet-auto",
    "symbols": [
        "BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT",
        "ADAUSDT", "DOTUSDT", "LINKUSDT", "MATICUSDT", "AVAXUSDT",
        "TRXUSDT", "LTCUSDT", "UNIUSDT", "ATOMUSDT", "DOGEUSDT"
    ],
    "trade_amount_usdt": 15.0,  # قيمة كل صفقة تلقائية (15 دولار)
    "maxDrawdownPercent": 5,
    "stopLossLimit": 10.0
}

# سجل لتتبع حالة الصفقات المفتوحة في الخلفية لمنع التكرار
active_trades = {symbol: False for symbol in BotConfig["symbols"]}
trade_logs = []

# 1. محرك التداول التلقائي الخوارزمي الذي يعمل في الخلفية (Background Task)
async def hft_trading_loop():
    await asyncio.sleep(5)  # انتظار بدء تشغيل السيرفر بالكامل
    while True:
        if not API_KEY or not SECRET_KEY:
            await asyncio.sleep(10)
            continue
        try:
            client = await AsyncClient.create(api_key=API_KEY, api_secret=SECRET_KEY, testnet=True)
            all_tickers = await client.get_all_tickers()
            
            prices = {t['symbol']: float(t['price']) for t in all_tickers if t['symbol'] in BotConfig["symbols"]}
            
            # هنا يوضع منطق الاستراتيجية التلقائية (كمثال: محاكي اقتناص الفرص عند التغير)
            for symbol, price in prices.items():
                # شرط الشراء الآلي: إذا كانت العملة غير مشتراة حالياً، يقرر البوت دخول صفقة تجريبية
                if not active_trades[symbol]:
                    try:
                        # حساب كمية العملة بناءً على المبلغ المحدد (15 دولار)
                        qty = round(BotConfig["trade_amount_usdt"] / price, 4)
                        if qty > 0:
                            order = await client.create_order(
                                symbol=symbol, side='BUY', type='MARKET', quantity=qty
                            )
                            active_trades[symbol] = True
                            trade_logs.append(f"🤖 AUTO-BUY: Mapped {qty} of {symbol} at ${price}")
                    except Exception as order_error:
                        pass # تجاهل الأخطاء الناتجة عن قيود حجم اللوت الأدنى للمنصة
            
            await client.close_connection()
        except Exception as e:
            trade_logs.append(f"⚠️ Loop Warning: Connection temporary glitch")
        
        await asyncio.sleep(5) # فحص السوق وتكرار العملية تلقائياً كل 5 ثوانٍ

# تشغيل محرك الصفقات التلقائي فور إقلاع السيرفر السحابي
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(hft_trading_loop())

# 2. واجهة الـ API لنقل البيانات وتحديث الشاشة
@app.get("/api/data")
async def get_live_data_api():
    prices_dict = {}
    account_balance = "0.00"
    try:
        client = await AsyncClient.create(api_key=API_KEY, api_secret=SECRET_KEY, testnet=True)
        all_tickers = await client.get_all_tickers()
        for ticker in all_tickers:
            if ticker['symbol'] in BotConfig["symbols"]:
                prices_dict[ticker['symbol']] = ticker['price']
                
        if API_KEY and SECRET_KEY:
            account_info = await client.get_account()
            for asset in account_info['balances']:
                if asset['asset'] == 'USDT':
                    account_balance = asset['free']
                    break
        await client.close_connection()
        return {"prices": prices_dict, "balance": account_balance, "logs": trade_logs[-5:]}
    except:
        return {"prices": {}, "balance": "Error", "logs": []}

# 3. واجهة التحكم الشاملة مع شاشة تتبع العمليات الآلية المباشرة
@app.get("/", response_class=HTMLResponse)
async def dashboard():
    table_rows = ""
    for symbol in BotConfig["symbols"]:
        table_rows += f"""
        <tr>
            <td>🪙 {symbol}</td>
            <td id="price-{symbol}" style="color: #f3ba2f; font-weight: bold;">Fetching...</td>
        </tr>
        """
    html_content = f"""
    <html>
        <head>
            <title>{BotConfig["bot_name"]}</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #121212; color: #ffffff; padding: 20px; direction: ltr; }}
                .container {{ max-width: 700px; margin: auto; background: #1e1e1e; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.5); }}
                h1 {{ color: #f3ba2f; border-bottom: 2px solid #333; padding-bottom: 10px; text-align: center; }}
                .metric-box {{ display: flex; justify-content: space-between; background: #2a2a2a; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                .shield-active {{ border-left: 5px solid #f3ba2f; padding-left: 10px; }}
                .log-box {{ background: #000; color: #00ff00; padding: 15px; font-family: Courier, monospace; height: 120px; overflow-y: auto; border-radius: 5px; border: 1px solid #333; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #333; }}
                th {{ background-color: #2a2a2a; color: #f3ba2f; }}
            </style>
            <script>
                async function updateDashboard() {{
                    try {{
                        let response = await fetch('/api/data');
                        let data = await response.json();
                        if (data.prices) {{
                            for (let symbol in data.prices) {{
                                let priceEl = document.getElementById('price-' + symbol);
                                if (priceEl) priceEl.innerText = "$" + parseFloat(data.prices[symbol]).toFixed(4);
                            }}
                        }}
                        if(!isNaN(data.balance)) {{
                            document.getElementById('live-balance').innerText = parseFloat(data.balance).toFixed(2) + " USDT";
                        }}
                        // تحديث شاشة سجل العمليات التلقائية المباشرة
                        let logBox = document.getElementById('log-box');
                        logBox.innerHTML = data.logs.length > 0 ? data.logs.join("<br>") : "Scanning market for automated trade signals...";
                    }} catch (err) {{}}
                }}
                setInterval(updateDashboard, 3000);
                window.onload = updateDashboard;
            </script>
        </head>
        <body>
            <div class="container">
                <h1>🛡️ {BotConfig["bot_name"]}</h1>
                <p style="text-align: center; color: #00ff00;"><strong>PRO SHIELD Automated HFT Loop Active</strong></p>
                
                <div class="metric-box shield-active" style="border-left-color: #00ff00;">
                    <span>Auto-Fetched Capital (Binance Spot):</span>
                    <strong id="live-balance" style="color: #00ff00;">Loading...</strong>
                </div>

                <h2>🤖 Real-Time Execution Engine Status (Live Logs)</h2>
                <div id="log-box" class="log-box">Initializing automated scanners...</div>

                <h2>📈 Monitored Assets</h2>
                <table>
                    <thead><tr><th>Asset Pair</th><th>Live Market Price</th></tr></thead>
                    <tbody>{table_rows}</tbody>
                </table>
            </div>
        </body>
    </html>
    """
    return html_content

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
