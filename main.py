import os
import asyncio
import threading
from flask import Flask
from binance import AsyncClient, BinanceSocketManager

app = Flask(__name__)

bot_stats = {
    "status": "⚙️ Running Radar...",
    "total_trades": 0,
    "simulated_balance_usdt": 10000.0,
    "net_profit_usdt": 0.0,
    "last_trade": "No trades captured yet"
}

@app.route('/')
def home():
    html = f"""
    <html>
        <head>
            <meta http-equiv="refresh" content="1">
            <title>HFT V2 - Flexible Mainnet Trader</title>
            <style>
                body {{ font-family: 'Courier New', monospace; background: #0a0a0a; color: #00ff00; padding: 20px; text-align: center; }}
                .dashboard {{ border: 2px solid #333; padding: 25px; display: inline-block; background: #111; border-radius: 8px; text-align: left; min-width: 400px; }}
                h2 {{ color: #ffcc00; text-align: center; margin-top: 0; }}
                .metric {{ color: #00ffff; font-weight: bold; }}
                .profit {{ color: #5cb85c; font-weight: bold; }}
                .danger {{ color: #d9534f; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="dashboard">
                <h2>📊 لوحة القيادة المالية - HFT V2</h2>
                <p><b>حالة الرادار:</b> {bot_stats['status']}</p>
                <hr style="border-color:#222;">
                <p>💵 الرصيد الحالي: <span class="metric">{bot_stats['simulated_balance_usdt']:.2f} USDT</span></p>
                <p>📈 صافي الأرباح/الخسائر: <span class="{'profit' if bot_stats['net_profit_usdt'] >= 0 else 'danger'}">{bot_stats['net_profit_usdt']:.4f} USDT</span></p>
                <p>🔄 إجمالي العمليات المنفذة: <span class="metric">{bot_stats['total_trades']} صفقة ثلاثية</span></p>
                <hr style="border-color:#222;">
                <p>🎯 <b>آخر عملية قنص:</b> <br><span style="color: #aaa; font-size: 12px;">{bot_stats['last_trade']}</span></p>
            </div>
        </body>
    </html>
    """
    return html

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, use_reloader=False)

API_KEY = os.getenv('BINANCE_API_KEY')
SECRET_KEY = os.getenv('BINANCE_SECRET_KEY')

TRIANGLE_PAIRS = ["BTCUSDT", "DOTBTC", "DOTUSDT"]
streams = [f"{pair.lower()}@ticker" for pair in TRIANGLE_PAIRS]

prices = {pair: 0.0 for pair in TRIANGLE_PAIRS}
trade_lock = False

async def execute_virtual_arbitrage(p1, p2, p3):
    global trade_lock
    trade_lock = True
    
    simulated_return = (1.0 / p1) / p2 * p3
    fee_factor = 0.003
    net_return = simulated_return - fee_factor
    
    trade_size = 1000.0
    profit_usdt = (net_return - 1.0) * trade_size
    
    if simulated_return > 1.0000:
        bot_stats["total_trades"] += 1
        bot_stats["simulated_balance_usdt"] += profit_usdt
        bot_stats["net_profit_usdt"] += profit_usdt
        bot_stats["last_trade"] = f"Success! Captured Opportunity, Return: {profit_usdt:.4f} USDT"
    
    await asyncio.sleep(0.02)
    trade_lock = False

async def run_hft_mainnet_core():
    global prices
    bot_stats["status"] = "Connecting to Binance..."
    
    client = await AsyncClient.create(API_KEY, SECRET_KEY)
    bm = BinanceSocketManager(client)
    multiplex_socket = bm.multiplex_socket(streams)
    
    bot_stats["status"] = "Live Market Radar Active - Sub-Milliseconds Tracking!"

    async with multiplex_socket as stream:
        while True:
            try:
                res = await stream.recv()
                if res and 'data' in res:
                    data = res['data']
                    pair_name = data['s']
                    current_close = float(data['c'])
                    
                    if pair_name in prices:
                        prices[pair_name] = current_close
                        p1, p2, p3 = prices["BTCUSDT"], prices["DOTBTC"], prices["DOTUSDT"]
                        
                        if p1 > 0 and p2 > 0 and p3 > 0 and not trade_lock:
                            asyncio.create_task(execute_virtual_arbitrage(p1, p2, p3))
            except Exception:
                await asyncio.sleep(0.01)

def start_core_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_hft_mainnet_core())

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    start_core_loop()
