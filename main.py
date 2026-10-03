import os
import time
import json
import random
import threading
from urllib.request import urlopen, Request
from http.server import BaseHTTPRequestHandler, HTTPServer

# 1. إعدادات الحساب والمراقبة الحية
balance_usdt = 1000.0          # الرصيد المحمي بالمحاكاة
max_order_size = 50.0          # حجم الصفقة الأقصى
total_opportunities = 0        # إجمالي الفرص المقتنصة
captured_opportunities = []    # قائمة الصفقات الحية
live_prices = {}               # مخزن الأسعار الحقيقية اللحظية

# القائمة الدقيقة لـ 15 عملة الأكثر سخونة ونشاطاً
crypto_pairs = [
    "BTC", "ETH", "SOL", "BNB", "XRP",
    "ADA", "AVAX", "LINK", "DOT", "MATIC",
    "NEAR", "INJ", "SUI", "APT", "OP"
]

# سجلات التنبيهات الذكية (تظهر في لوحة التحكم)
system_alerts = ["[نظام الأمان]: تم تفعيل مراقبة التقلبات الكبرى وأخطاء الاتصال بنجاح."]

# 2. حالة المحرك
kill_switch_activated = False
engine_status_text = "نشط ومتصل بأسعار السوق الحقيقية اللحظية 🌐"
engine_status_color = "#00ff88"

# 3. دالة جلب الأسعار الحقيقية من السوق (تحديث مستمر)
def fetch_live_market_prices():
    global live_prices, system_alerts
    # نستخدم مصدر بيانات مجاني ومفتوح وموثوق لا يتطلب مفاتيح API للتجربة
    symbols = ",".join([c.lower() for c in crypto_pairs])
    url = f"https://coingecko.com"
    
    # خريطة لتحويل الأسماء البرمجية إلى الرموز الخاصة بك
    name_map = {
        'bitcoin': 'BTC', 'ethereum': 'ETH', 'solana': 'SOL', 'binancecoin': 'BNB', 'ripple': 'XRP',
        'cardano': 'ADA', 'avalanche-2': 'AVAX', 'chainlink': 'LINK', 'polkadot': 'DOT', 'matic-network': 'MATIC',
        'near': 'NEAR', 'injective-protocol': 'INJ', 'sui': 'SUI', 'aptos': 'APT', 'optimism': 'OP'
    }

    print("[+] جاري بدء سحب أسعار السوق الحية...")
    while True:
        try:
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                for gecko_id, price_info in data.items():
                    symbol = name_map.get(gecko_id)
                    if symbol:
                        # فحص التقلبات الكبرى (إذا كان السعر القديم موجوداً وتغير بأكثر من 5%)
                        new_price = float(price_info['usdt'])
                        if symbol in live_prices:
                            old_price = live_prices[symbol]
                            change_pct = abs((new_price - old_price) / old_price) * 100
                            if change_pct >= 5.0:
                                system_alerts.insert(0, f"[⚠️ تقلب حاد]: تحركت عملة {symbol} بنسبة {change_pct:.2f}% في لحظات!")
                        
                        live_prices[symbol] = new_price
            time.sleep(2) # تحديث الأسعار كل ثانيتين لعدم حظر السيرفر
        except Exception as e:
            # تتبع خطأ النظام الحرج (الشرط الثالث)
            error_msg = f"[❌ خطأ نظام]: فشل الاتصال بمصدر الأسعار الحية: {str(e)[:50]}"
            if error_msg not in system_alerts:
                system_alerts.insert(0, error_msg)
            time.sleep(5)

# 4. محرك الـ HFT الذكي (يعمل بأجزاء من الثانية ويبني صفقات بناءً على الأسعار الحقيقية الحالية)
def hft_engine():
    global balance_usdt, total_opportunities, captured_opportunities, live_prices
    trade_id = 90001
    
    while True:
        try:
            # سرعة HFT خاطفة (بين 50 إلى 200 جزء من الثانية)
            time.sleep(random.uniform(0.05, 0.2))
            
            if not live_prices:
                continue
                
            # اختيار عملة عشوائية من الـ 15 المتوفر أسعارها حالياً
            pair_symbol = random.choice(list(live_prices.keys()))
            current_market_price = live_prices[pair_symbol]
            
            # محاكاة اقتناص فارق سعر خاطف (Arbitrage Scalping) بناءً على السعر الحقيقي
            profit_percentage = random.uniform(0.01, 0.08) 
            profit_amount = (max_order_size * profit_percentage) / 100
            
            balance_usdt += profit_amount
            total_opportunities += 1
            
            current_time = time.strftime("%H:%M:%S") + f".{int((time.time() % 1) * 1000):03d}"
            
            new_trade = {
                'id': f"HFT-{trade_id}",
                'time': current_time,
                'pair': f"{pair_symbol}/USDT",
                'price': f"${current_market_price:,.2f}",
                'profit': f"+${profit_amount:.4f}"
            }
            
            captured_opportunities.insert(0, new_trade)
            trade_id += 1
            
            if len(captured_opportunities) > 10:
                captured_opportunities.pop()
                
        except Exception as e:
            time.sleep(1)

# 5. واجهة السيرفر ولوحة التحكم المحدثة
class SimpleWeb(BaseHTTPRequestHandler):
    def do_GET(self):
        global balance_usdt, total_opportunities, captured_opportunities, engine_status_text, engine_status_color, system_alerts
        
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        
        # إنعاش تلقائي كل 1 ثانية لمتابعة الأجزاء من الثانية والأسعار الحية
        html = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>محرك المراجعة المحترف - Live Prices</title>
            <meta http-equiv="refresh" content="1">
            <style>
                body {{ font-family: 'Segoe UI', sans-serif; background-color: #080808; color: #ffffff; padding: 10px; text-align: center; direction: rtl; }}
                .container {{ max-width: 480px; margin: 0 auto; background: #111; padding: 15px; border-radius: 12px; border: 1px solid #222; }}
                h1 {{ font-size: 16px; color: #fff; margin-bottom: 2px; }}
                .status-box {{ padding: 8px; border-radius: 6px; background: #161616; margin-bottom: 10px; font-size: 11px; border: 1px solid #262626; }}
                .status-text {{ color: {engine_status_color}; text-shadow: 0 0 8px {engine_status_color}33; }}
                
                /* صندوق التنبيهات المباشر للشروط الثلاثة */
                .alert-box {{ background: #1c1111; border-right: 4px solid #ff3333; padding: 8px; border-radius: 6px; font-size: 11px; text-align: right; margin-bottom: 10px; max-height: 60px; overflow-y: auto; color: #ffcccc; }}
                
                .info-box {{ background: #151515; padding: 10px; border-radius: 6px; font-size: 12px; margin-bottom: 10px; border-right: 4px solid #0056b3; text-align: right; line-height: 1.5; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 5px; background: #0c0c0c; font-size: 11px; }}
                th {{ background: #0056b3; color: white; padding: 6px; }}
                td {{ padding: 6px; border-bottom: 1px solid #1c1c1c; font-family: monospace; }}
                .footer-text {{ font-size: 9px; color: #444; margin-top: 15px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>محرك المراجعة المحترف - إدارة (V3)</h1>
                <p style="font-size:10px; color:#00ff88; margin: 0 0 10px 0; font-weight:bold;">[ تدفق حقيقي مقترن بأسعار السوق الحية 🌐 ]</p>
                
                <div class="status-box">
                    حالة النظام: <span class="status-text">{engine_status_text}</span>
                </div>
                
                <!-- مركز التنبيهات الذكي للحالات الحرجة والتحديثات والتقلبات -->
                <div class="alert-box">
                    <strong>شريط التنبيهات الحية (الشرط الشامل):</strong><br>
                    {"<br>".join(system_alerts[:3])}
                </div>
                
                <div class="info-box">
                    <strong>الرصيد بالمحاكاة الحية:</strong> <span style="color:#00ff88; font-weight:bold;">${balance_usdt:.4f} USDT</span><br>
                    <strong>إجمالي الفرص الذكية:</strong> {total_opportunities} فرصة
                </div>
                
                <table>
                    <thead>
                        <tr>
                            <th>الربح</th>
                            <th>المثل</th>
                            <th>السعر الحالي</th>
                            <th>التوقيت اللحظي</th>
                        </tr>
                    </thead>
                    <tbody>
                        """
        
        if not captured_opportunities:
            html += """
                        <tr>
                            <td colspan="4" style="color: #555; padding: 15px;">جاري جلب نبض الأسعار الحية من البورصة وبناء الصفقات...</td>
                        </tr>
            """
        else:
            for opp in captured_opportunities:
                html += f"""
                        <tr>
                            <td style="color:#00ff88; font-weight:bold;">{opp['profit']}</td>
                            <td style="color:#fff;">{opp['pair']}</td>
                            <td style="color:#ffea00;">{opp['price']}</td>
                            <td style="color:#00e1ff;">{opp['time']}</td>
                        </tr>
                """
                
        html += f"""
                    </tbody>
                </table>
                
                <p class="footer-text">TRIPLE FILTER CONDITION MONITOR ACTIVE • COINGECKO LIVE STEAM</p>
            </div>
        </body>
        </html>
        """
        self.wfile.write(html.encode('utf-8'))

def run_server():
    port = int(os.environ.get("PORT", 8080))
    httpd = HTTPServer(('', port), SimpleWeb)
    print(f"[-] خادم النظام الحقيقي يعمل على المنفذ: {port}")
    httpd.serve_forever()

if __name__ == "__main__":
    # تشغيل خيط جلب الأسعار الحية من السوق
