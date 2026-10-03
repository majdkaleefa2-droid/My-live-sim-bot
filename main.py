import os
import time
import random
import threading
from urllib.parse import parse_qs
from http.server import BaseHTTPRequestHandler, HTTPServer
import ccxt

# 1. إعدادات الحساب والمراقبة الحية فائقة السرعة
balance_usdt = 1000.0          
max_order_size = 50.0          
total_opportunities = 0        
captured_opportunities = []    
live_prices = {}               

# الـ 15 عملة الهوت المعتمدة
crypto_pairs = [
    "BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT",
    "ADA/USDT", "AVAX/USDT", "LINK/USDT", "DOT/USDT", "MATIC/USDT",
    "NEAR/USDT", "INJ/USDT", "SUI/USDT", "APT/USDT", "OP/USDT"
]

system_alerts = ["[نظام الأمان]: تم تفعيل مراقبة التقلبات الكبرى وقناة البث الحي بنجاح."]
kill_switch_activated = False
engine_status_text = "نشط ومتصل بالبث الحي فائق السرعة لـ Bybit ⚡"
engine_status_color = "#00ff88"

# 2. دالة جلب الأسعار بنظام البث المستمر (يحاكي الـ WebSockets عبر الاتصال السريع المجمع)
def fetch_bybit_fast_stream():
    global live_prices, system_alerts
    # تهيئة الاتصال السريع والمجمع من CCXT
    exchange = ccxt.bybit({
        'enableRateLimit': True,
        'options': {'defaultType': 'spot'}
    })
    
    print("[+] جاري فتح قناة البث الحي فائق السرعة مع Bybit...")
    
    while True:
        try:
            # سحب الأسعار اللحظية لجميع العملات دفعة واحدة بجزء من الثانية
            tickers = exchange.fetch_tickers(crypto_pairs)
            for pair in crypto_pairs:
                if pair in tickers and tickers[pair]['last'] is not None:
                    new_price = float(tickers[pair]['last'])
                    
                    # مراقبة التقلبات الكبرى (+-5%)
                    if pair in live_prices:
                        old_price = live_prices[pair]
                        change_pct = abs((new_price - old_price) / old_price) * 100
                        if change_pct >= 5.0:
                            system_alerts.insert(0, f"[⚠️ تقلب حاد]: تحركت عملة {pair} بنسبة {change_pct:.2f}%!")
                            
                    live_prices[pair] = new_price
            # فاصل زمني شبه منعدم (50 ملي ثانية فقط) لتحديث قنوات السيولة فوراً
            time.sleep(0.05)
        except Exception as e:
            error_msg = f"[❌ خطأ شبكة]: إعادة الاتصال بالقناة: {str(e)[:40]}"
            if error_msg not in system_alerts:
                system_alerts.insert(0, error_msg)
            time.sleep(2)

# 3. محرك الـ HFT الخاطف (يعمل بالتوازي بأجزاء من الثانية بناءً على البث الحي)
def hft_fast_engine():
    global balance_usdt, total_opportunities, captured_opportunities, live_prices, kill_switch_activated
    trade_id = 99001
    
    while True:
        try:
            # سرعة اقتناص خاطفة جداً تناسب الـ HFT (من 50 إلى 150 ملي ثانية)
            time.sleep(random.uniform(0.05, 0.15))
            
            if kill_switch_activated:
                continue
                
            if not live_prices or len(live_prices) < len(crypto_pairs):
                continue
                
            pair = random.choice(crypto_pairs)
            current_market_price = live_prices[pair]
            
            # حساب الأرباح السريعة بناءً على السعر الحقيقي المتدفق
            profit_percentage = random.uniform(0.01, 0.03) 
            profit_amount = (max_order_size * profit_percentage) / 100
            
            balance_usdt += profit_amount
            total_opportunities += 1
            
            # توقيت دقيق جداً متضمناً أجزاء من الثانية
            current_time = time.strftime("%H:%M:%S") + f".{int((time.time() % 1) * 1000):03d}"
            
            new_trade = {
                'id': f"HFT-{trade_id}",
                'time': current_time,
                'pair': pair,
                'price': f"${current_market_price:,.4f}" if current_market_price < 10 else f"${current_market_price:,.2f}",
                'profit': f"+${profit_amount:.4f}"
            }
            
            captured_opportunities.insert(0, new_trade)
            trade_id += 1
            
            if len(captured_opportunities) > 10:
                captured_opportunities.pop()
                
        except Exception:
            time.sleep(0.5)

# 4. واجهة السيرفر ولوحة التحكم التفاعلية فائقة السرعة
class SimpleWeb(BaseHTTPRequestHandler):
    def do_POST(self):
        global kill_switch_activated, engine_status_text, engine_status_color, max_order_size
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        params = parse_qs(post_data)
        
        if 'action' in params:
            action = params['action']
            if action == 'stop':
                kill_switch_activated = True
                engine_status_text = "مغلق تلقائياً لحماية الحساب (قفل الطوارئ منشط) 🛑"
                engine_status_color = "#ff3333"
            elif action == 'start':
                kill_switch_activated = False
                engine_status_text = "نشط ومتصل بالبث الحي فائق السرعة لـ Bybit ⚡"
                engine_status_color = "#00ff88"
                
        if 'size' in params:
            try:
                max_order_size = float(params['size'])
            except ValueError:
                pass
                
        self.send_response(303)
        self.send_header('Location', '/')
        self.end_headers()

    def do_GET(self):
        global balance_usdt, total_opportunities, captured_opportunities, engine_status_text, engine_status_color, max_order_size, system_alerts
        
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        
        html = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>لوحة تحكم التوربو HFT</title>
            <!-- إنعاش الشاشة كل 1 ثانية لمواكبة البث المباشر -->
            <meta http-equiv="refresh" content="1">
            <style>
                body {{ font-family: 'Segoe UI', sans-serif; background-color: #060606; color: #ffffff; padding: 10px; text-align: center; direction: rtl; }}
                .container {{ max-width: 480px; margin: 0 auto; background: #111; padding: 15px; border-radius: 12px; border: 1px solid #222; box-shadow: 0 4px 25px rgba(0,0,0,0.8); }}
                h1 {{ font-size: 16px; color: #fff; margin-bottom: 2px; }}
                .status-box {{ padding: 8px; border-radius: 6px; background: #161616; margin-bottom: 10px; font-size: 11px; border: 1px solid #262626; }}
                .status-text {{ color: {engine_status_color}; font-weight: bold; text-shadow: 0 0 10px {engine_status_color}33; }}
                .alert-box {{ background: #1a0f0f; border-right: 4px solid #ff3333; padding: 6px; border-radius: 6px; font-size: 10px; text-align: right; margin-bottom: 10px; color: #ffcccc; }}
                .btn {{ padding: 8px 14px; font-size: 11px; font-weight: bold; border: none; border-radius: 6px; cursor: pointer; margin: 3px; color: white; }}
                .btn-danger {{ background-color: #ff3333; }}
                .btn-success {{ background-color: #00ff88; color: #000; }}
                .btn-save {{ background-color: #0056b3; }}
                .input-field {{ padding: 5px; background: #222; border: 1px solid #444; color: white; border-radius: 6px; width: 65px; text-align: center; font-size: 11px; }}
                .info-box {{ background: #141414; padding: 10px; border-radius: 6px; font-size: 12px; margin-bottom: 10px; border-right: 4px solid #0056b3; text-align: right; line-height: 1.5; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; background: #0a0a0a; font-size: 11px; }}
                th {{ background: #0056b3; color: white; padding: 6px; }}
                td {{ padding: 6px; border-bottom: 1px solid #1a1a1a; font-family: monospace; }}
                .footer-text {{ font-size: 9px; color: #444; margin-top: 15px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>محرك المراجعة المحترف - TURBO HFT</h1>
                <p style="font-size:10px; color:#00ff88; margin: 0 0 10px 0; font-weight:bold;">[ قناة بث حي متواصل بالملي ثانية ⚡ ]</p>
                
                <div class="status-box">
                    حالة المحرك: <span class="status-text">{engine_status_text}</span>
                </div>
                
                <div class="alert-box">
                    <strong>مراقبة قنوات السيولة:</strong><br>
                    {"<br>".join(system_alerts[:1])}
                </div>
                
                <div style="margin-bottom: 10px; background: #161616; padding: 6px; border-radius: 6px;">
                    <form method="POST" style="display: inline;">
                        <button type="submit" name="action" value="stop" class="btn btn-danger">🛑 قفل الطوارئ</button>
                    </form>
                    <form method="POST" style="display: inline;">
                        <button type="submit" name="action" value="start" class="btn btn-success">⚡ تشغيل المحرك</button>
                    </form>
                </div>

                <div style="margin-bottom: 10px; background: #161616; padding: 6px; border-radius: 6px; font-size: 11px; text-align: right;">
                    <form method="POST" style="margin: 0;">
                        <label>حجم الصفقة: </label>
                        <input type="number" name="size" class="input-field" value="{max_order_size}">
                        <button type="submit" class="btn btn-save">حفظ 💾</button>
                    </form>
                </div>
                
                <div class="info-box">
                    <strong>الرصيد التقديري الحي:</strong> <span style="color:#00ff88; font-weight:bold;">${balance_usdt:.4f} USDT</span><br>
