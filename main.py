import asyncio
import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

BotConfig = {
    "bot_name": "HFT_V7_PULSE_RIDER_PRO_SHIELD",
    "version": "7.9.9",
    "symbols": [
        "BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT",
        "ADAUSDT", "DOTUSDT", "LINKUSDT", "MATICUSDT", "AVAXUSDT"
    ],
    "trade_amount_usdt": 20.0,
    "take_profit_pct": 1.0,
    "stop_loss_pct": 1.5
}

# الذاكرة المحلية لتخزين نتائج التداول الوهمي
trade_history = []
active_positions = []
total_pnl = 0.0

# استقبال تحديثات الصفقات والأسعار مباشرة من المتصفح ومعالجتها
@app.post("/api/update")
async def update_bot_logic(request: Request):
    global total_pnl
    data = await request.json()
    prices = data.get("prices", {})
    
    # محاكاة الاستراتيجية الخوارزمية المتكاملة بناءً على الأسعار الحية المجلوبة من المتصفح
    if prices and len(active_positions) < 3:
        for symbol, price in prices.items():
            price_float = float(price)
            # إذا لم تكن هناك صفقات مفتوحة لهذه العملة، يتم الشراء آلياً
            if not any(pos['symbol'] == symbol for pos in active_positions):
                qty = round(BotConfig["trade_amount_usdt"] / price_float, 4)
                active_positions.append({
                    "symbol": symbol,
                    "buy_price": price_float,
                    "quantity": qty
                })
                
    # فحص شروط البيع التلقائي (جني الأرباح ووقف الخسارة)
    for pos in active_positions[:]:
        sym = pos["symbol"]
        if sym in prices:
            current_p = float(prices[sym])
            change = ((current_p - pos["buy_price"]) / pos["buy_price"]) * 100
            
            if change >= BotConfig["take_profit_pct"] or change <= -BotConfig["stop_loss_pct"]:
                pnl = (current_p - pos["buy_price"]) * pos["quantity"]
                total_pnl += pnl
                status = "✅ PROFIT" if pnl > 0 else "❌ LOSS"
                trade_history.append(f"{status} | {sym} | PnL: ${pnl:.2f} ({change:.2f}%)")
                active_positions.remove(pos)

    return {
        "total_pnl": f"{total_pnl:.2f}",
        "trades_count": len(trade_history),
        "history": trade_history[-5:],
        "active_positions": [f"🔄 {p['symbol']} from ${p['buy_price']}" for p in active_positions]
    }

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    table_rows = ""
    for symbol in BotConfig["symbols"]:
        table_rows += f"<tr><td>🪙 {symbol}</td><td id='price-{symbol}' style='color: #f3ba2f; font-weight: bold;'>Fetching...</td></tr>"
        
    html_template = """
    <html>
        <head>
            <title>{{BOT_NAME}}</title>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; background-color: #121212; color: #ffffff; padding: 20px; direction: ltr; }
                .container { max-width: 650px; margin: auto; background: #1e1e1e; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.5); }
                h1 { color: #f3ba2f; border-bottom: 2px solid #333; padding-bottom: 10px; text-align: center; }
                .pnl-container { display: flex; gap: 10px; margin-bottom: 15px; }
                .card { flex: 1; background: #2a2a2a; padding: 15px; border-radius: 5px; text-align: center; border-bottom: 4px solid #f3ba2f; }
                .log-title { margin-top: 20px; font-size: 1.2em; color: #f3ba2f; border-left: 3px solid #f3ba2f; padding-left: 8px; }
                .display-box { background: #000; color: #00ff00; padding: 12px; font-family: monospace; border-radius: 5px; min-height: 80px; border: 1px solid #333; margin-top: 5px; font-size: 0.95em; }
                table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                th, td { padding: 12px; text-align: left; border-bottom: 1px solid #333; }
                th { background-color: #2a2a2a; color: #f3ba2f; }
            </style>
            <script>
                const symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT", "DOTUSDT", "LINKUSDT", "MATICUSDT", "AVAXUSDT"];
                
                async function fetchPricesDirectlyFromBinance() {
                    let localPrices = {};
                    try {
                        // متصفحك يجلب الأسعار مباشرة من خادم بينانس العام بدون حظر IP
                        let response = await fetch("https://binance.com");
                        let data = await response.json();
                        
                        data.forEach(ticker => {
                            if(symbols.includes(ticker.symbol)) {
                                localPrices[ticker.symbol] = ticker.price;
                                let el = document.getElementById('price-' + ticker.symbol);
                                if(el) el.innerText = "$" + parseFloat(ticker.price).toFixed(2);
                            }
                        });
                        
                        // إرسال الأسعار الحية المجلوبة إلى البوت في السيرفر لمعالجة الصفقة
                        let botResponse = await fetch('/api/update', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ prices: localPrices })
                        });
                        let botData = await botResponse.json();
                        
                        // تحديث شاشة العرض بناءً على معالجة المحرك
                        document.getElementById('wallet-cap').innerText = "10,000.00 USDT (Demo)";
                        document.getElementById('pnl-stat').innerText = (botData.total_pnl >= 0 ? "+" : "") + botData.total_pnl + " USDT";
                        document.getElementById('pnl-stat').style.color = botData.total_pnl >= 0 ? "#00ff00" : "#ff3333";
                        document.getElementById('count-stat').innerText = botData.trades_count;
                        
                        document.getElementById('active-box').innerHTML = botData.active_positions.length > 0 ? botData.active_positions.join("<br>") : "Scanning assets...";
                        document.getElementById('history-box').innerHTML = botData.history.length > 0 ? botData.history.reverse().join("<br>") : "Waiting for signals...";
                        
                    } catch(e) {
                        console.log("Binance API fetch error", e);
                    }
                }
                setInterval(fetchPricesDirectlyFromBinance, 2000); // تحديث شامل وفتح صفقات كل ثانيتين
                window.onload = fetchPricesDirectlyFromBinance;
            </script>
        </head>
        <body>
            <div class="container">
                <h1>🛡️ {{BOT_NAME}}</h1>
                <p style="text-align: center; color: #00ff00; font-weight: bold; margin-top: -10px;">PRO SHIELD Cloud Non-Blocked Execution Engine</p>
                
                <div class="pnl-container">
                    <div class="card" style="border-bottom-color: #00ff00;">
                        <div style="font-size: 0.9em; color: #aaa;">Spot Wallet</div>
                        <div id="wallet-cap" style="font-size: 1.3em; font-weight: bold; margin-top: 5px;">Loading...</div>
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
                    <tbody>{{TABLE_ROWS}}</tbody>
                </table>
            </div>
        </body>
    </html>
    """
    output = html_template.replace("{{BOT_NAME}}", BotConfig["bot_name"])
    output = output.replace("{{TABLE_ROWS}}", table_rows)
    return output

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
