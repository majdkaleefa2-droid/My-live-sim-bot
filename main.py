import asyncio
import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from binance import AsyncClient
import uvicorn

app = FastAPI()

# سحب المفاتيح الآمنة التي أدخلتها أنت سابقاً في Railway
API_KEY = os.environ.get("BINANCE_API_KEY", "")
SECRET_KEY = os.environ.get("BINANCE_SECRET_KEY", "")

BotConfig = {
    "bot_name": "HFT_V7_PULSE_RIDER_PRO_SHIELD",
    "version": "7.1.0",
    "environment": "binance-spot-testnet",
    "symbol": "BTCUSDT",
    "maxDrawdownPercent": 5,
    "stopLossLimit": 10.0
}

# 1. دالة جلب البيانات المتوافقة مع محفظة الـ Spot التجريبية
@app.get("/api/data")
async def get_live_data_api():
    live_price = "Connecting..."
    account_balance = "0.00"
    
    try:
        # الاتصال ببينانس وتحديد شبكة الـ Spot التجريبية الحية
        client = await AsyncClient.create(api_key=API_KEY, api_secret=SECRET_KEY, testnet=True)
        
        # جلب السعر الحي للبيتكوين
        ticker = await client.get_symbol_ticker(symbol=BotConfig["symbol"])
        live_price = ticker['price']
        
        # جلب رصيد محفظة الـ Spot الفعلي تلقائياً
        if API_KEY and SECRET_KEY:
            account_info = await client.get_account()
            for asset in account_info['balances']:
                if asset['asset'] == 'USDT':
                    account_balance = asset['free']
                    break
        else:
            account_balance = "Config Check Required"
            
        await client.close_connection()
        return {"price": live_price, "balance": account_balance}
    except Exception as e:
        return {"price": "Error", "balance": "Spot Auth Failed"}

# 2. واجهة التحكم الاحترافية بالتحديث اللحظي
@app.get("/", response_class=HTMLResponse)
async def dashboard():
    html_content = f"""
    <html>
        <head>
            <title>{BotConfig["bot_name"]}</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #121212; color: #ffffff; padding: 20px; direction: ltr; }}
                .container {{ max-width: 600px; margin: auto; background: #1e1e1e; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.5); }}
                h1 {{ color: #f3ba2f; border-bottom: 2px solid #333; padding-bottom: 10px; }}
                .metric-box {{ display: flex; justify-content: space-between; background: #2a2a2a; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                .shield-active {{ border-left: 5px solid #f3ba2f; padding-left: 10px; }}
            </style>
            <script>
                async function updateDashboardData() {{
                    try {{
                        let response = await fetch('/api/data');
                        let data = await response.json();
                        
                        if(data.price !== "Error" && data.price !== "Connecting...") {{
                            document.getElementById('live-price').innerText = "$" + parseFloat(data.price).toFixed(2);
                        }} else {{
                            document.getElementById('live-price').innerText = data.price;
                        }}
                        
                        if(!isNaN(data.balance)) {{
                            let balanceVal = parseFloat(data.balance);
                            document.getElementById('live-balance').innerText = balanceVal.toFixed(2) + " USDT";
                            let drawdownVal = (balanceVal * {BotConfig["maxDrawdownPercent"]}) / 100;
                            document.getElementById('drawdown-val').innerText = drawdownVal.toFixed(2) + " USDT";
                        }} else {{
                            document.getElementById('live-balance').innerText = data.balance;
                        }}
                        
                    }} catch (err) {{
                        document.getElementById('live-price').innerText = "Reconnecting...";
                    }}
                }}
                setInterval(updateDashboardData, 2000);
                window.onload = updateDashboardData;
            </script>
        </head>
        <body>
            <div class="container">
                <h1>🛡️ {BotConfig["bot_name"]} - V7 PRO SHIELD</h1>
                <p><strong>System Status:</strong> <span style="color: #00ff00;">Connected to Binance Spot Test Network</span></p>
                <p><strong>Environment:</strong> {BotConfig["environment"]}</p>
                
                <div class="metric-box">
                    <span>Monitored Symbol:</span>
                    <strong>{BotConfig["symbol"]}</strong>
                </div>
                <div class="metric-box">
                    <span>Live Market Price (Binance API):</span>
                    <strong id="live-price" style="color: #f3ba2f;">Fetching...</strong>
                </div>
                
                <h2>Live Account Financial Metrics</h2>
                <div class="metric-box shield-active" style="border-left-color: #00ff00;">
                    <span>Auto-Fetched Capital (Binance Spot):</span>
                    <strong id="live-balance" style="color: #00ff00;">Loading Spot Wallet...</strong>
                </div>
                <div class="metric-box shield-active">
                    <span>Dynamic Max Allowed Drawdown (5%):</span>
                    <span id="drawdown-val">Calculating...</span>
                </div>
                <div class="metric-box shield-active">
                    <span>Total Stop Loss Limit:</span>
                    <span>{BotConfig["stopLossLimit"]} USDT</span>
                </div>
            </div>
        </body>
    </html>
    """
    return html_content

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
