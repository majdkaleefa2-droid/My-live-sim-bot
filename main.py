import asyncio
import os
import time
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from binance import AsyncClient
import uvicorn

app = FastAPI()

# سحب المفاتيح الآمنة من إعدادات Railway
API_KEY = os.environ.get("BINANCE_API_KEY", "")
SECRET_KEY = os.environ.get("BINANCE_SECRET_KEY", "")

BotConfig = {
    "bot_name": "HFT_V7_PULSE_RIDER_PRO_SHIELD",
    "version": "7.9.0",
    "environment": "binance-spot-testnet-full",
    "symbols": [
        "BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT",
        "ADAUSDT", "DOTUSDT", "LINKUSDT", "MATICUSDT", "AVAXUSDT"
    ],
    "trade_amount_usdt": 20.0,  # قيمة المغامرة في كل صفقة (20 دولار)
    "take_profit_pct": 1.0,     # جني الأرباح تلقائياً عند +1%
    "stop_loss_pct": 1.5,       # وقف الخسارة تلقائياً لحمايتك عند -1.5%
    "maxDrawdownPercent": 5
}

# الهياكل البرمجية لتتبع الصفقات والأرباح في الذاكرة الحية
portfolio_positions = {symbol: None for symbol in BotConfig["symbols"]} 
closed_trades = []
total_pnl_usdt = 0.0
total_trades_count = 0

# محرك التداول الآلي بالكامل (البيع والشراء التلقائي المتكامل)
async def fully_automated_hft_engine():
    global total_pnl_usdt, total_trades_count
    await asyncio.sleep(5) # انتظار استقرار السيرفر السحابي
    
    while True:
        if not API_KEY or not SECRET_KEY:
            await asyncio.sleep(5)
            continue
            
        try:
            client = await AsyncClient.create(api_key=API_KEY, api_secret=SECRET_KEY, testnet=True)
            all_tickers = await client.get_all_tickers()
            current_prices = {t['symbol']: float(t['price']) for t in all_tickers if t['symbol'] in BotConfig["symbols"]}
            
            for symbol, price in current_prices.items():
                position = portfolio_positions[symbol]
                
                # 1. منطق البيع التلقائي (الخروج من الصفقة لحاله)
                if position is not None:
                    buy_price = position["buy_price"]
                    qty = position["quantity"]
                    
                    # حساب النسبة المئوية للتغير الحالي في السعر
                    price_change_pct = ((price - buy_price) / buy_price) * 100
                    
                    # فحص شروط الأمان وجني الأرباح
                    triggered_tp = price_change_pct >= BotConfig["take_profit_pct"]
                    triggered_sl = price_change_pct <= -BotConfig["stop_loss_pct"]
                    
                    if triggered_tp or triggered_sl:
                        try:
                            # إرسال أمر بيع فوري لسوق بينانس التجريبي
                            order = await client.create_order(
                                symbol=symbol, side='SELL', type='MARKET', quantity=qty
                            )
                            
                            # حساب صافي الربح أو الخسارة المحقق بالدولار
                            trade_pnl = (price - buy_price) * qty
                            total_pnl_usdt += trade_pnl
                            total_trades_count += 1
                            
                            status_label = "✅ PROFIT" if trade_pnl > 0 else "❌ LOSS"
                            closed_trades.append(
                                f"{status_label} | {symbol} | PnL: ${trade_pnl:.2f} ({price_change_pct:.2f}%)"
                            )
                            
                            # إفراغ المركز للسماح بصفقات جديدة
                            portfolio_positions[symbol] = None
                        except:
                            pass
                            
                # 2. منطق الشراء التلقائي (اقتناص الفرص الفوري لحاله)
                else:
                    try:
                        qty = round(BotConfig["trade_amount_usdt"] / price, 4)
                        if qty > 0:
                            order = await client.create_order(
                                symbol=symbol, side='BUY', type='MARKET', quantity=qty
                            )
                            # تسجيل تفاصيل الدخول لمراقبتها في الدورة القادمة
                            portfolio_positions[symbol] = {
                                "buy_price": price,
                                "quantity": qty,
                                "timestamp": time.time()
                            }
                    except:
                        pass
                        
            await client.close_connection()
        except:
            pass
            
        await asyncio.sleep(3) # إعادة مسح السوق بالكامل وإدارة المراكز كل 3 ثوانٍ

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(fully_automated_hft_engine())

# واجهة البرمجية لنقل النتائج اللحظية للشاشة
@app.get("/api/results")
async def get_results_api():
    account_balance = "0.00"
    try:
        client = await AsyncClient.create(api_key=API_KEY, api_secret=SECRET_KEY, testnet=True)
        if API_KEY and SECRET_KEY:
            account_info = await client.get_account()
            for asset in account_info['balances']:
                if asset['asset'] == 'USDT':
                    account_balance = asset['free']
                    break
        await client.close_connection()
    except:
        account_balance = "Connection Error"
        
    # تجميع المراكز المفتوحة حالياً لعرضها
    active_positions_list = []
    for sym, pos in portfolio_positions.items():
        if pos:
            active_positions_list.append(f"🔄 {sym} active from ${pos['buy_price']}")
            
    return {
        "balance": account_balance,
        "total_pnl": f"{total_pnl_usdt:.2f}",
        "trades_count": total_trades_count,
        "history": closed_trades[-6:],
        "active_positions": active_positions_list
    }

# واجهة العرض الرسومية الشاملة لكافة النتائج
@app.get("/", response_class=HTMLResponse)
async def dashboard():
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
                .active-box {{ color: #38bdf8; }}
            </style>
            <script>
                async function refreshBotMetrics() {{
                    try {{
                        let response = await fetch('/api/results');
                        let data = await response.json();
                        
                        document.getElementById('wallet-cap').innerText = parseFloat(data.balance).toFixed(2) + " USDT";
                        
                        let pnlEl = document.getElementById('pnl-stat');
                        pnlEl.innerText = (data.total_pnl >= 0 ? "+" : "") + data.total_pnl + " USDT";
                        pnlEl.style.color = data.total_pnl >= 0 ? "#00ff00" : "#ff3333";
                        
                        document.getElementById('count-stat').innerText = data.trades_count;
                        
                        // تحديث الصفقات الجارية والمغلقة
                        document.getElementById('active-box').innerHTML = data.active_positions.length > 0 ? data.active_positions.join("<br>") : "No active trades. Scanning market...";
                        document.getElementById('history-box').innerHTML = data.history.length > 0 ? data.history.reverse().join("<br>") : "Waiting for first execution lifecycle to close...";
                    }} catch(e) {{}}
                }}
                setInterval(refreshBotMetrics, 2000);
                window.onload = refreshBotMetrics;
            </script>
        </head>
        <body>
            <div class="container">
                <h1>🛡️ {BotConfig["bot_name"]}</h1>
                <p style="text-align: center; color: #00ff00; font-weight: bold; margin-top: -10px;">PRO SHIELD End-to-End Live Execution Engine</p>
                
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
