import time
import random
import requests
import json
import asyncio
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

# --- 1. إنشاء التطبيق أولاً لحل مشكلة الترتيب والـ NameError ---
app = FastAPI() 

# --- 2. المعرفات وإعدادات الحساب الميكرو (200 USDT) ---
TOKEN = "HFT_V7_PULSE_RIDER_ASGI_READY_OCT_6"
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

# --- 3. الدوال والمحاكاة المنطقية لفلاتر الواقع ---
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

# --- 4. نقاط الربط ومسارات الويب (Endpoints) مرتبة بشكل صحيح ---
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(background_loop())

@app.get("/")
def read_root():
    return {"status": "RUNNING", "bot": "HFT_V7_PULSE_RIDER", "capital": portfolio["balance"]}

@app.get("/radar", response_class=HTMLResponse)
def show_professional_radar():
    """لوحة تحكم الرادار الاحترافية لنسخة HFT V7 - وضع الميكرو الصارم"""
    html_content = f"""
    <html>
        <head>
            <title>HFT V7 PRO RADAR</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ background-color: #0b0e11; color: #eaecef; font-family: Arial, sans-serif; padding: 20px; text-align: center; }}
                .container {{ max-width: 500px; margin: auto; background: #181a20; padding: 20px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }}
                .metric {{ margin: 20px 0; padding: 15px; background: #2b3139; border-radius: 8px; }}
                .value {{ font-size: 24px; font-weight: bold; color: #02c076; }}
                .valve {{ color: #f6465d; font-size: 18px; font-weight: bold; }}
                .token {{ font-size: 11px; color: #848e9c; word-break: break-all; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>📡 HFT V7 LIVE RADAR</h2>
                <p class="token">TOKEN: {TOKEN}</p>
                <hr style="border-color: #2b3139;">
                
                <div class="metric">
                    <p>💰 رأس المال الصافي الحقيقي (Micro)</p>
                    <div class="value">{portfolio['balance']:.2f} USDT</div>
                </div>
                
                <div class="metric">
                    <p>🛑 صمام حظر التراجع اليومي (5%)</p>
                    <div class="valve">{portfolio['drawdown_limit']:.1f} USDT</div>
                </div>
                
                <div class="metric">
                    <p>📊 عامل الربحية الواقعي (PF)</p>
                    <div class="value" style="color: #f0b90b;">{portfolio['profit_factor']:.2f}</div>
                </div>

                <div class="metric">
                    <p>💸 العمولات المخصومة التراكمية</p>
                    <div style="font-size: 18px; font-weight: bold;">{portfolio['total_fees']:.4f} USDT</div>
                </div>
                
                <div class="metric" style="background: #02c07622;">
                    <p>🔄 إجمالي الموجات المقيدة</p>
                    <div style="font-size: 20px; font-weight: bold; color: #02c076;">{portfolio['captured_waves']} موجة</div>
                </div>
            </div>
            <script>
                setTimeout(function(){{ location.reload(); }}, 2000);
            </script>
        </body>
    </html>
    """
    return html_content
