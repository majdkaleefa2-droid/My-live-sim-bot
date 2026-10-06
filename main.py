import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

BotConfig = {
    "bot_name": "HFT_V7_PULSE_RIDER_PRO_SHIELD",
    "version": "9.9.0",
    "symbols": ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"]
}

@app.get("/api/health")
async def health_check():
    # دالة بسيطة للرد على السيرفر ليتأكد أن التطبيق حي ولا يغلقه
    return {"status": "healthy", "bot": BotConfig["bot_name"]}

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    table_rows = ""
    for symbol in BotConfig["symbols"]:
        table_rows += f"<tr><td>🪙 {symbol}</td><td id='price-{symbol}' style='color: #f3ba2f; font-weight: bold;'>Connecting...</td></tr>"
        
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
                const symbolsList = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"];
                
                async function updatePrices() {{
                    try {{
                        // جلب الأسعار مباشرة من جهازك لتفادي حظر السيرفر تماماً
                        let response = await fetch("https://binance.com");
                        let data = await response.json();
                        
                        data.forEach(ticker => {{
                            if(symbolsList.includes(ticker.symbol)) {{
                                let el = document.getElementById('price-' + ticker.symbol);
                                if(el) el.innerText = "$" + parseFloat(ticker.price).toFixed(2);
                            }}
                        }});
                        
                        document.getElementById('core-status').innerText = "Active (Cloud Stable)";
                        document.getElementById('core-status').style.color = "#00ff00";
                    }} catch (err) {{
                        document.getElementById('core-status').innerText = "Retrying Connection...";
                        document.getElementById('core-status').style.color = "#ff3333";
                    }}
                }}
                setInterval(updatePrices, 2000);
                window.onload = updatePrices;
            </script>
        </head>
        <body>
            <div class="container">
                <h1>🛡️ {BotConfig["bot_name"]}</h1>
                <p style="text-align: center; color: #00ff00;"><strong>PRO SHIELD Cloud Infrastructure Stable</strong></p>
                
                <div class="metric-box">
                    <span>Engine Status:</span>
                    <strong id="core-status" style="color: #f3ba2f;">Connecting to Core...</strong>
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
