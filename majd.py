import asyncio
import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from binance import AsyncClient
import uvicorn

app = FastAPI()

BotConfig = {
    "bot_name": "HFT_V7_PULSE_RIDER_PRO_SHIELD",
    "version": "7.0.0",
    "environment": "binance-testnet-simulation",
    "symbol": "BTCUSDT",
    "baseCapital": 200.00,
    "maxDrawdownPercent": 5,
    "stopLossLimit": 10.0
}

# 1. نقطة نهاية (Endpoint) خاصة بإعادة السعر فقط على هيئة JSON للتحديث اللحظي
@app.get("/api/price")
async def get_price_api():
    try:
        client = await AsyncClient.create()
        ticker = await client.get_symbol_ticker(symbol=BotConfig["symbol"])
        await client.close_connection()
        return {"price": ticker['price']}
    except:
        return {"price": "Error Connecting"}

# 2. واجهة التحكم المحسنة بالتحديث اللحظي الذكي
@app.get("/", response_class=HTMLResponse)
async def dashboard():
    max_drawdown_val = (BotConfig["baseCapital"] * BotConfig["maxDrawdownPercent"]) / 100
    
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
                // دالة جافا سكريبت لجلب السعر في الخلفية وتحديث الشاشة كل ثانية
                async function updatePrice() {{
                    try {{
                        let response = await fetch('/api/price');
                        let data = await response.json();
                        document.getElementById('live-price').innerText = "$" + parseFloat(data.price).toFixed(2);
                    }} catch (err) {{
                        document.getElementById('live-price').innerText = "Reconnecting...";
                    }}
                }}
                // تشغيل التحديث التلقائي كل 1000 مللي ثانية (ثانية واحدة)
                setInterval(updatePrice, 1000);
                window.onload = updatePrice;
            </script>
        </head>
        <body>
            <div class="container">
                <h1>🛡️ {BotConfig["bot_name"]} - V7 PRO SHIELD</h1>
                <p><strong>System Status:</strong> <span style="color: #00ff00;">Running Securely (Sandbox Mode)</span></p>
                <p><strong>Environment:</strong> {BotConfig["environment"]}</p>
                
                <div class="metric-box">
                    <span>Monitored Symbol:</span>
                    <strong>{BotConfig["symbol"]}</strong>
                </div>
                <div class="metric-box">
                    <span>Live Market Price (Binance API):</span>
                    <strong id="live-price" style="color: #f3ba2f;">Fetching...</strong>
                </div>
                
                <h2>Active Risk Management Controls</h2>
                <div class="metric-box shield-active">
                    <span>Max Allowed Drawdown:</span>
                    <span>{BotConfig["maxDrawdownPercent"]}% (${max_drawdown_val} USDT)</span>
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
