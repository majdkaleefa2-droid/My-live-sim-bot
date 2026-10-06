import time
import random
import requests
import json
import asyncio
from fastapi import FastAPI # أضفنا هذا لإنشاء متغير التطبيق المطلوب

# --- حل مشكلة السيرفر (ASGI app) ---
app = FastAPI() # هذا هو المتغير "app" الذي يبحث عنه سيرفر Railway لإصلاح الخطأ 🎯

TOKEN = "HFT_V7_PULSE_RIDER_MICRO_REAL_SIM_OCT_6"
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

# --- نقطة فحص برمجية للسيرفر للتأكد من عمله ---
@app.get("/")
def read_root():
    return {"status": "RUNNING", "bot": "HFT_V7_PULSE_RIDER", "capital": portfolio["balance"]}

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
        res = requests.get(f"{TESTNET_API_URL}/v3/ticker/price", params={"symbol": symbol})
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

# دالة التشغيل المستقلة في الخلفية
async def background_loop():
    print(f"🚀 تم بدء تشغيل الفحص الخلفي الصارم برأس مال {MICRO_CAPITAL} USDT...")
    while True:
        latency = get_network_latency()
        status = "MOMENTUM_INVERSION" if latency <= LATENCY_LIMIT_MS else "SAFETY_LOCK_ACTIVATED"
        
        if status == "MOMENTUM_INVERSION":
            for pair in HOT_PAIRS:
                bids, asks = get_real_market_depth(pair)
                if bids > asks * 1.5:  
                    result = process_hft_trade(pair, "BUY")
                    if result == "CRITICAL_HALT":
                        print("🚨 صمام التراجع تفعل!")
                        break
        
        # طباعة مباشرة في السجلات (Logs) للرصد المباشر
        print(f"📋 Balance: {portfolio['balance']:.2f} | PF: {portfolio['profit_factor']:.2f} | Ping: {latency:.1f}ms")
        await asyncio.sleep(2)

# تشغيل الحلقة الخلفية تلقائياً عند إقلاع السيرفر
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(background_loop())
