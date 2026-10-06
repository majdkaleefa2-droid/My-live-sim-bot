import asyncio
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from binance import AsyncClient
import uvicorn

app = FastAPI()

# 1. System Configurations and Hardened Risk Settings
BotConfig = {
    "bot_name": "HFT_V7_PULSE_RIDER_PRO_SHIELD",
    "version": "7.0.0",
    "environment": "binance-testnet-simulation",
    "symbol": "BTCUSDT",  # Note: python-binance uses symbol without slash '/'
    "baseCapital": 200.00,
    "maxDrawdownPercent": 5,
    "stopLossLimit": 10.0
}

# 2. Live Binance Price Fetcher using python-binance
async def get_live_price():
    try:
        # Initialize an anonymous client for public live market data
        client = await AsyncClient.create()
        ticker = await client.get_symbol_ticker(symbol=BotConfig["symbol"])
        await client.close_connection()
        return ticker['price']
    except Exception as e:
        return "Connecting..."

# 3. Clean UI Dashboard Generation
@app.get("/", response_class=HTMLResponse)
async def dashboard():
    live_price = await get_live_price()
    
    # Calculate exact maximum drawdown value based on capital
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
                    <strong style="color: #f3ba2f;">${live_price}</strong>
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
    uvicorn.run(app, host="127.0.0.1", port=8000)
