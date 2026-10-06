import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

BotConfig = {
    "bot_name": "HFT_V7_PULSE_RIDER_PRO_SHIELD",
    "version": "8.0.0",
    "symbols": ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT", "DOTUSDT", "LINKUSDT", "MATICUSDT", "AVAXUSDT"]
}

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
                .pnl-container {{ display: flex; gap: 10px; margin-bottom: 15px; }}
                .card {{ flex: 1; background: #2a2a2a; padding: 15px; border-radius: 5px; text-align: center; border-bottom: 4px solid #f3ba2f; }}
                .log-title {{ margin-top: 20px; font-size: 1.2em; color: #f3ba2f; border-left: 3px solid #f3ba2f; padding-left: 8px; }}
                .display-box {{ background: #000; color: #00ff00; padding: 12px; font-family: monospace; border-radius: 5px; min-height: 80px; border: 1px solid #333; margin-top: 5px; font-size: 0.95em; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #333; }}
                th {{ background-color: #2a2a2a; color: #f3ba2f; }}
            </style>
            <script>
                const targetSymbols = {BotConfig["symbols"]};
                let activeTrades = [];
                let tradeHistory = [];
                let totalPnL = 0.0;
                let initialBalance = 10000.00;

                async function runEngine() {{
                    try {{
                        // جلب مباشر وآمن 100% للأسعار من خادم بينانس العام إلى متصفحك
                        let response = await fetch("https://binance.com");
                        let data = await response.json();
                        
                        let currentPrices = {{}};
                        data.forEach(ticker => {{
                            if(targetSymbols.includes(ticker.symbol)) {{
                                currentPrices[ticker.symbol] = parseFloat(ticker.price);
                                let el = document.getElementById('price-' + ticker.symbol);
                                if(el) el.innerText = "$" + currentPrices[ticker.symbol].toFixed(2);
                            }}
                        }});

                        document.getElementById('wallet-cap').innerText = (initialBalance + totalPnL).toFixed(2) + " USDT";

                        // منطق فتح الصفقات تلقائياً (شراء وهمي عند توفر السعر)
                        if (activeTrades.length < 3) {{
                            for (let sym of targetSymbols) {{
                                if (currentPrices[sym] && !activeTrades.some(t => t.symbol === sym)) {{
                                    activeTrades.push({{
                                        symbol: sym,
                                        buyPrice: currentPrices[sym],
                                        quantity: 20.0 / currentPrices[sym]
                                    }});
                                }}
                            }}
                        }}

                        // منطق البيع وجني الأرباح / وقف الخسارة
                        for (let i = activeTrades.length - 1; i >= 0; i--) {{
                            let trade = activeTrades[i];
                            if (currentPrices[trade.symbol]) {{
                                let curPrice = currentPrices[trade.symbol];
                                let changePct = ((curPrice - trade.buyPrice) / trade.buyPrice) * 100;

                                if (changePct >= 0.5 || changePct <= -0.8) {{
                                    let pnl = (curPrice - trade.buyPrice) * trade.quantity;
                                    totalPnL += pnl;
                                    let status = pnl >= 0 ? "✅ PROFIT" : "❌ LOSS";
                                    tradeHistory.push(status + " | " + trade.symbol + " | PnL: $" + pnl.toFixed(2) + " (" + changePct.toFixed(2) + "%)");
                                    activeTrades.splice(i, 1);
                                }}
                            }}
                        }}

                        // تحديث الشاشات الرسومية
                        let pnlEl = document.getElementById('pnl-stat');
                        pnlEl.innerText = (totalPnL >= 0 ? "+" : "") + totalPnL.toFixed(2) + " USDT";
                        pnlEl.style.color = totalPnL >= 0 ? "#00ff00" : "#ff3333";
                        
                        document.getElementById('count-stat').innerText = tradeHistory.length;
                        
                        document.getElementById('active-box').innerHTML = activeTrades.length > 0 ? 
                            activeTrades.map(t => "🔄 " + t.symbol + " active from $" + t.buyPrice.toFixed(2)).join("<br>") : "Scanning assets...";
                            
                        document.getElementById('history-box').innerHTML = tradeHistory.length > 0 ? 
                            tradeHistory.slice(-5).reverse().join("<br>") : "Waiting for signals...";

                    }} catch(e) {{
                        console.log(e);
                    }}
                }}
                
                setInterval(runEngine, 2000);
                window.onload = runEngine;
            </script>
        </head>
        <body>
            <div class="container">
                <h1>🛡️ {BotConfig["bot_name"]}</h1>
                <p style="text-align: center; color: #00ff00; font-weight: bold; margin-top: -10px;">PRO SHIELD Client-Side Simulated Core Active</p>
                
                <div class="pnl-container">
                    <div class="card" style="border-bottom-color: #00ff00;">
                        <div style="font-size: 0.9em; color: #aaa;">Spot Wallet</div>
                        <div id="wallet-cap" style="font-size: 1.3em; font-weight: bold; margin-top: 5px;">10000.00 USDT</div>
                    </div>
                    <div class="card">
                        <div style="font-size: 0.9em; color: #aaa;">Net Profit/PnL</div>
                        <div id="pnl-stat" style="font-size: 1.3em; font-weight: bold; margin-top: 5px;">$0.00</div>
                    </div>
                    <div class="card" style="border-bottom-color: #38bdf8;">
                        <div style="font-size: 0.9em; color: #aaa;">Closed Trades</div>
                        <div id="count-stat" style="font-size: 1.3em; font-weight: bold; margin-top: 5px;">0</div>
                    </div>
                </div>

                <div class="log-title">🔄 Active Market Positions (Current Trades)</div>
                <div id="active-box" class="display-box" style="color: #38bdf8;">Scanning assets...</div>

                <div class="log-title">📋 Performance Real-Time Analytics (Closed Logs)</div>
                <div id="history-box" class="display-box">Waiting for signals...</div>

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
