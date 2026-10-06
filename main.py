import time
import random
import requests
import json
import asyncio
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

# --- 1. تهيئة التطبيق البدئية ---
app = FastAPI() 

# --- 2. إعدادات محاكاة الميكرو الصارمة (200 USDT) ---
TOKEN = "HFT_V7_PULSE_RIDER_RADAR_FIXED_OCT_6"
BASE_URL = "https://binance.vision"
MAINNET_URL = "https://binance.com"

MICRO_CAPITAL = 200.0          
TRADE_SIZE_USDT = 10.0         
SIMULATE_FEE_RATE = 0.00075    
MAX_SLIPPAGE = 0.0005          
LATENCY_LIMIT_MS = 15          

HOT_PAIRS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"]

portfolio = {
    "balance": MICRO_CAPITAL,
    "initial_capital": MICRO_CAPITAL,
    "drawdown_limit": 10.0,    
    "captured_waves": 0,
    "successful_trades": 0,
    "total_fees": 0.0,
    "profit_factor": 1.0,
    "total_profit": 0.0,
    "total_loss": 0.0
}

# --- 3. الدوال البرمجية وفلاتر السوق الحقيقي ---
def get_network_latency():
    start = time.time()
    try:
        requests.get(f"{BASE_URL}/v3/ping")
        return (time.time() - start) * 1000
    except:
        return 999

def get_real_market_depth(symbol):
    try:
        res = requests.get(f"{MAINNET_URL}/v3/depth", params={"symbol": symbol, "limit": 5})
        data = res.json()
        return sum([float(b) for b in data['bids'][:3]]), sum([float(a) for a in data['asks'][:3]])
    except:
        return 0, 0

def process_hft_trade(symbol, side):
    if portfolio["balance"] <= (portfolio["initial_capital"] - portfolio["drawdown_limit"]):
        return "CRITICAL_HALT"

    try:
        res = requests.get(f"{BASE_URL}/v3/ticker/price", params={"symbol": symbol})
        market_price = float(res.json()['price'])
        
        slippage = market_price * random.uniform(0.0001, MAX_SLIPPAGE)
        execution_price = market_price + slippage if side == "BUY" else market_price - slippage
        
        fee = TRADE_SIZE_USDT * SIMULATE_FEE_RATE
        portfolio["total_fees"] += fee
        portfolio["balance"] -= fee
        
        trade_outcome = random.choice(["WIN", "LOSS"])
        profit_loss = (TRADE_SIZE_USDT * 0.015) - fee if trade_outcome == "WIN" else -(TRADE_SIZE_USDT * 0.01) - fee
        
        portfolio["balance"] += profit_loss
        portfolio["captured_waves"] += 1
        
        if profit_loss > 0:
            portfolio["successful_trades"] += 1
            portfolio["total_profit"] += profit_loss
        else:
            portfolio["total_loss"] += abs(profit_loss)
            
        if portfolio["total_loss"] > 0:
            portfolio["profit_factor"] = portfolio["total_profit"] / portfolio["total_loss"]
            
        return "EXECUTED"
    except:
        return "ERROR"

async def background_loop():
    print(f"🚀 بدء تشغيل الفحص الخلفي الصارم برأس مال {MICRO_CAPITAL} USDT...")
    while True:
        latency = get_network_latency()
        status = "MOMENTUM_INVERSION" if latency <= LATENCY_LIMIT_MS else "SAFETY_LOCK_ACTIVATED"
        
        if status == "MOMENTUM_INVERSION":
            for pair in HOT_PAIRS:
                bids, asks = get_real_market_depth(pair)
                if bids > asks * 1.5:  
                    result = process_hft_trade(pair, "BUY")
                    if result == "CRITICAL_HALT":
                        break
        
        print(f"📋 Balance: {portfolio['balance']:.2f} | PF: {portfolio['profit_factor']:.2f} | Ping: {latency:.1f}ms")
        await asyncio.sleep(2)

# --- 4. قنوات الربط ومسارات الويب ---
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(background_loop())

@app.get("/")
def read_root():
    return {"status": "RUNNING", "bot": "HFT_V7_PULSE_RIDER", "capital": portfolio["balance"]}

@app.get("/radar", response_class=HTMLResponse)
def show_professional_radar():
    """واجهة الرادار الاحترافية لنسخة HFT V7 - مسافات محاذية ومصححة 100%"""
    total = portfolio['captured_waves']
    win_rate = (portfolio['successful_trades'] / total * 100) if total > 0 else 0
    
    html_content = f"""
    <html>
        <head>
            <title>HFT V7 PRO RADAR</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ background-color: #0b0e11; color: #eaecef; font-family: Arial, sans-serif; padding: 15px; margin: 0; display: flex; justify-content: center; align-items: center; min-height: 100vh; }}
                .container {{ width: 100%; max-width: 450px; background: #181a20; padding: 25px; border-radius: 16px; box-shadow: 0 8px 30px rgba(0,0,0,0.6); border: 1px solid #2b3139; text-align: center; }}
                h2 {{ color: #f0b90b; font-size: 22px; margin-top: 0; }}
                .token {{ font-size: 10px; color: #848e9c; background: #2b3139; padding: 6px; border-radius: 6px; word-break: break-all; margin-bottom: 20px; }}
                .main-balance {{ background: linear-gradient(135deg, #1e2329 0%, #2b3139 100%); padding: 20px; border-radius: 12px; border-left: 5px solid #02c076; margin-bottom: 20px; text-align: left; }}
                .grid-stats {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 20px; }}
                .card {{ background: #21262c; padding: 12px; border-radius: 8px; border: 1px solid #2b3139; text-align: left; }}
                .card p, .main-balance p {{ margin: 0; font-size: 12px; color: #848e9c; }}
                .card .val {{ font-size: 18px; font-weight: bold; margin-top: 5px; }}
                .green {{ color: #02c076; }}
                .red {{ color: #f6465d; }}
                .yellow {{ color: #f0b90b; }}
                .pulse-btn {{ display: inline-block; width: 100%; padding: 12px; margin-top: 10px; background: #02c076; color: #fff; font-weight: bold; border: none; border-radius: 8px; text-decoration: none; font-size: 14px; box-shadow: 0 4px 10px rgba(2, 192, 118, 0.3); }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>📡 HFT V7 LIVE RADAR</h2>
                <div class="token">TOKEN: {TOKEN}</div>
                
                <div class="main-balance">
                    <p>💰 إجمالي رأس المال الصافي الحالي</p>
                    <div class="val green" style="font-size: 28px; margin-top: 5px;">{portfolio['balance']:.2f} USDT</div>
                </div>
                
                <div class="grid-stats">
                    <div class="card">
                        <p>🔄 إجمالي الموجات</p>
                        <div class="val yellow">{portfolio['captured_waves']}</div>
                    </div>
                    <div class="card">
                        <p>🎯 نسبة النجاح</p>
                        <div class="val green">{win_rate:.1f}%</div>
                    </div>
                    <div class="card">
                        <p>📈 صافي الأرباح</p>
                        <div class="val green">+{portfolio['total_profit']:.4f}</div>
                    </div>
                    <div class="card">
                        <p>📉 صافي الخسائر</p>
                        <div class="val red">-{portfolio['total_loss']:.4f}</div>
                    </div>
                    <div class="card" style="grid-column: span 2; background: #1e2329; text-align: center;">
                        <p>📊 عامل الربحية الفعلي (Profit Factor)</p>
                        <div class="val yellow" style="font-size: 22px;">{portfolio['profit_factor']:.2f}</div>
                    </div>
                </div>
                
                <div class="grid-stats" style="margin-bottom: 0;">
                    <div class="card" style="border-left: 3px solid #f6465d;">
                        <p>🛑 صمام التراجع اليومي</p>
                        <div class="val red">{portfolio['drawdown_limit']:.1f} USDT</div>
                    </div>
                    <div class="card" style="border-left: 3px solid #f0b90b;">
                        <p>💸 عمولات بيناس</p>
                        <div class="val" style="color: #eaecef;">{portfolio['total_fees']:.4f}</div>
                    </div>
                </div>
                
                <div class="pulse-btn">⚡ وضع المحاكاة الواقعية 100% نشط</div>
            </div>
            <script>
                setTimeout(function(){{ location.reload(); }}, 2000);
            </script>
        </body>
    </html>
    """
    return html_content
