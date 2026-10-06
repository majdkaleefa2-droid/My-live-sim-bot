import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

BotConfig = {
    "bot_name": "HFT_V7_PULSE_RIDER_PRO_SHIELD",
    "version": "9.5.0",
    "environment": "railway-hybrid-core",
    "symbols": ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"]
}

@app.get("/api/status")
async def get_status():
    # التحقق محلياً من وجود المتغيرات في السيرفر
    has_keys = "Configured" if os.environ.get("BINANCE_API_KEY") else "Missing Keys"
    return {"status": "Active", "keys": has_keys}

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    table_rows = ""
    for symbol in BotConfig["symbols"]:
        table_rows += f"<tr><td>🪙 {symbol}</td><td id='price-{symbol}' style='color: #f3ba2f; font-weight: bold;'>Fetching Live...</td></tr>"
        
    html_content = f"""
    <html>
        <head>
            <title>{BotConfig["bot_name"]}</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #121212; color: #ffffff; padding: 20px; direction: ltr; }}
                .container {{ max-width: 650px; margin: auto; background: #1e1e1e; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.5); }}
                h1 {{ color: #f3ba2f; border-bottom: 2px solid #333; padding-bottom: 10px; text-align: center; }}
                .metric-box {{ display: flex; justify-content: space-between; background: #2a2a2a; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 5px solid #00ff00; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #333; }}
                th {{ background-color: #2a2a2a; color: #f3ba2f; }}
            </style>
            <script>
                const trackedSymbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"];
                
                async function updateDashboardData() {{
                    try {{
                        // 1. المتصفح يجلب الأسعار الحية مباشرة عبر شبكتك المحلية بدون حظر IP
                        let binanceResponse = await fetch("https://binance.com");
                        let data = await binanceResponse.json();
                        
                        data.forEach(ticker => {{
                            if(trackedSymbols.includes(ticker.symbol)) {{
                                let el = document.getElementById('price-' + ticker.symbol);
                                if(el) el.innerText = "$" + parseFloat(ticker.price).toFixed(2);
                            }}
                        }});
                        
                        // 2. التحقق من حالة السيرفر
                        let statusResponse = await fetch('/api/status');
                        let statusData = await statusResponse.json();
                        document.getElementById('api-status').innerText = "Connected (" + statusData.keys + ")";
                        document.getElementById('api-status').style.color = "#00ff00";
                        
                    }} catch (err) {{
                        document.getElementById('api-status').innerText = "Connection Interrupted";
                        document.getElementById('api-status').style.color = "#ff3333";
                    }}
                }}
                setInterval(updateDashboardData, 2000);
                window.onload = updateDashboardData;
            </script>
        </head>
        <body>
            <div class="container">
                <h1>🛡️ {BotConfig["bot_name"]}</h1>
                <p style="text-align: center; color: #00ff00;"><strong>Hybrid Execution Core Active</strong></p>
                
                <div class="metric-box">
                    <span>Binance API Connection Status:</span>
                    <strong id="api-status" style="color: #f3ba2f;">Initializing Core...</strong>
                </div>

                <h2>📈 Spot Testnet Live Assets</h2>
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
