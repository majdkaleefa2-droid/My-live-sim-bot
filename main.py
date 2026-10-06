import os
import json
import urllib.request
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

BotConfig = {
    "bot_name": "HFT_V7_PULSE_RIDER_PRO_SHIELD",
    "version": "8.9.0",
    "symbols": ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT", "DOTUSDT", "LINKUSDT", "MATICUSDT", "AVAXUSDT"]
}

# 1. دالة جلب الأسعار باستخدام مكتبة بايثون المدمجة والنقية لمنع أي ModuleNotFoundError
@app.get("/api/realtime-prices")
async def get_prices():
    try:
        url = "https://binance.com"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        
        # فتح الاتصال البرمجي وقراءة البيانات الحية
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            
            prices_dict = {}
            for ticker in data:
                if ticker['symbol'] in BotConfig["symbols"]:
                    prices_dict[ticker['symbol']] = float(ticker['price'])
            return {"status": "success", "prices": prices_dict}
    except Exception as e:
        return {"status": "error", "message": str(e), "prices": {}}

# 2. الواجهة الرسومية الكاملة والمستقرة سحابياً
@app.get("/", response_class=HTMLResponse)
async def dashboard():
    table_rows = ""
    for symbol in BotConfig["symbols"]:
        table_rows += f"<tr><td>🪙 {symbol}</td><td id='price-{symbol}' class='price-field' style='color: #f3ba2f; font-weight: bold;'>Loading Live Data...</td></tr>"
        
    html_content = f"""
    <html>
        <head>
            <title>{BotConfig["bot_name"]}</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #121212; color: #ffffff; padding: 20px; direction: ltr; }}
                .container {{ max-width: 650px; margin: auto; background: #1e1e1e; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.5); }}
                h1 {{ color: #f3ba2f; border-bottom: 2px solid #333; padding-bottom: 10px; text-align: center; }}
                .pnl-container {{ display: flex; gap: 10px; margin-bottom: 15px; }}
                .card {{ flex: 1; background: #2a2a2a; padding: 15px; border-radius: 5px; text-align: center; border-bottom: 4px solid #f3ba2f; }}
                .log-title {{ margin-top: 20px; font-size: 1.2em; color: #f3ba2f; border-left: 3px solid #f3ba2f; padding-left: 8px; }}
                .display-box {{ background: #000; color: #00ff00; padding: 12px; font-family: monospace; border-radius: 5px; min-height: 80px; border: 1px solid #333; margin-top: 5px; font-size: 0.95em; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #333; }}
                th {{ background-color: #2a2a2a; color: #f3ba2f; }}
            </style>
            <script>
                async function updateDashboardData() {{
                    try {{
                        let response = await fetch('/api/realtime-prices');
                        let data = await response.json();
                        
                        if(data.status === "success" && data.prices) {{
                            for (let symbol in data.prices) {{
                                let el = document.getElementById('price-' + symbol);
                                if(el) el.innerText = "$" + parseFloat(data.prices[symbol]).toFixed(2);
                            }}
                        }} else {{
                            let fields = document.getElementsByClassName('price-field');
                            for (let i = 0; i < fields.length; i++) {{
                                fields[i].innerText = "API Blocked / Retrying...";
                            }}
                        }}
                    }} catch(e) {{
                        console.log(e);
                    }}
                }}
                setInterval(updateDashboardData, 3000);
                window.onload = updateDashboardData;
            </script>
        </head>
        <body>
            <div class="container">
                <h1>🛡️ {BotConfig["bot_name"]}</h1>
                <p style="text-align: center; color: #00ff00; font-weight: bold; margin-top: -10px;">PRO SHIELD Native Standard Core</p>
                
                <div class="pnl-container">
                    <div class="card" style="border-bottom-color: #00ff00;">
                        <div style="font-size: 0.9em; color: #aaa;">Spot Wallet</div>
                        <div style="font-size: 1.3em; font-weight: bold; margin-top: 5px;">10000.00 USDT</div>
                    </div>
                    <div class="card">
                        <div style="font-size: 0.9em; color: #aaa;">Net Profit/PnL</div>
                        <div style="font-size: 1.3em; font-weight: bold; margin-top: 5px; color: #00ff00;">$0.00</div>
                    </div>
                    <div class="card" style="border-bottom-color: #38bdf8;">
                        <div style="font-size: 0.9em; color: #aaa;">Closed Trades</div>
                        <div style="font-size: 1.3em; font-weight: bold; margin-top: 5px;">0</div>
                    </div>
                </div>

                <div class="log-title">🔄 Active Market Positions (Current Trades)</div>
                <div class="display-box" style="color: #38bdf8;">Scanning assets dynamically...</div>

                <div class="log-title">📋 Performance Real-Time Analytics (Closed Logs)</div>
                <div class="display-box">Waiting for execution lifecycle...</div>

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
