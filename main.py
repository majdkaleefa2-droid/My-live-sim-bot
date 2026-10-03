import os
import time
import random
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# 1. إعدادات الحساب والمحاكاة فائقة السرعة
balance_usdt = 1000.0          # الرصيد المحمي بالمحاكاة
max_order_size = 50.0          # حجم الصفقة الأقصى
total_opportunities = 0        # إجمالي الفرص المقتنصة
captured_opportunities = []    # قائمة الصفقات النشطة

# القائمة الدقيقة لـ 15 عملة الأكثر سخونة ونشاطاً (15 Hot Pairs) التي اعتمدناها
crypto_pairs = [
    "BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT",
    "ADA/USDT", "AVAX/USDT", "LINK/USDT", "DOT/USDT", "MATIC/USDT",
    "NEAR/USDT", "INJ/USDT", "SUI/USDT", "APT/USDT", "OP/USDT"
]

# 2. حالة المحرك
kill_switch_activated = False
engine_status_text = "نشط ويعمل بسرعة HFT (أجزاء من الثانية)"
engine_status_color = "#00ff88"

# 3. محرك HFT فائق السرعة المخصص لـ 15 عملة هوت
def hft_simulation_engine():
    global balance_usdt, total_opportunities, captured_opportunities
    trade_id = 70001
    
    print("[+] تم إطلاق محرك الـ HFT فائق السرعة لـ 15 عملة هوت...")
    
    while True:
        try:
            # الفاصل الزمني الخاطف بالأجزاء من الثانية (بين 0.05 إلى 0.2 ثانية)
            time.sleep(random.uniform(0.05, 0.2))
            
            # اقتناص الفرصة حصرياً من قائمة الـ 15 عملة النشطة
            pair = random.choice(crypto_pairs)
            
            # أرباح المراجع اللحظية الخاطفة (Scalping)
            profit_percentage = random.uniform(0.01, 0.15) 
            profit_amount = (max_order_size * profit_percentage) / 100
            
            # تحديث الحساب لحظياً
            balance_usdt += profit_amount
            total_opportunities += 1
            
            # تسجيل التوقيت الدقيق متضمناً أجزاء من الثانية (Milliseconds)
            current_time = time.strftime("%H:%M:%S") + f".{int((time.time() % 1) * 1000):03d}"
            
            new_trade = {
                'id': f"HFT-{trade_id}",
                'time': current_time,
                'pair': pair,
                'profit': f"+${profit_amount:.3f}"
            }
            
            # إدخال الصفقة في أعلى الجدول فوراً
            captured_opportunities.insert(0, new_trade)
            trade_id += 1
            
            # الحفاظ على آخر 12 صفقة فقط لضمان استقرار المعالجة والذاكرة
            if len(captured_opportunities) > 12:
                captured_opportunities.pop()
                
        except Exception as e:
            print(f"[!] خطأ في المحرك السريع: {e}")
            time.sleep(1)

# 4. واجهة السيرفر ولوحة التحكم
class SimpleWeb(BaseHTTPRequestHandler):
    def do_GET(self):
        global balance_usdt, total_opportunities, captured_opportunities, engine_status_text, engine_status_color
        
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        
        # تحديث الصفحة كل 1 ثانية في المتصفح لرؤية التدفق اللحظي
        html = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>محرك المراجعة المحترف - 15 Hot Pairs</title>
            <meta http-equiv="refresh" content="1">
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0c0c0c; color: #ffffff; padding: 15px; text-align: center; direction: rtl; }}
                .container {{ max-width: 500px; margin: 0 auto; background: #141414; padding: 20px; border-radius: 12px; border: 1px solid #222; box-shadow: 0 8px 30px rgba(0,0,0,0.7); }}
                h1 {{ font-size: 18px; color: #ffffff; margin-bottom: 5px; }}
                .status-box {{ padding: 10px; border-radius: 6px; background: #1c1c1c; margin-bottom: 15px; font-weight: bold; font-size: 12px; border: 1px solid #292929; }}
                .status-text {{ color: {engine_status_color}; text-shadow: 0 0 10px {engine_status_color}44; }}
                .info-box {{ background: #181818; padding: 12px; border-radius: 6px; font-size: 13px; margin-bottom: 15px; border-right: 4px solid #0056b3; text-align: right; line-height: 1.6; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; background: #111111; font-size: 12px; }}
                th {{ background: #0056b3; color: white; padding: 8px; font-weight: 600; }}
                td {{ padding: 8px; border-bottom: 1px solid #222; font-family: 'Courier New', Courier, monospace; }}
                .footer-text {{ font-size: 10px; color: #444; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>محرك المراجعة المحترف - إدارة (V3)</h1>
                <p style="font-size:10px; color:#00ff88; margin-top:0; margin-bottom:15px; font-weight:bold;">[ نظام HFT المطور • مسح 15 عملة هوت ]</p>
                
                <div class="status-box">
                    حالة المحرك (Kill Switch): <span class="status-text">{engine_status_text} ⚡</span>
                </div>
                
                <div class="info-box">
                    <strong>الرصيد المحمي بالمحاكاة:</strong> <span style="color:#00ff88; font-weight:bold;">${balance_usdt:.4f} USDT</span><br>
                    <strong>حجم الصفقة الأقصى:</strong> ${max_order_size:.2f} $<br>
                    <strong>إجمالي الفرص المقتنصة:</strong> {total_opportunities}
                </div>
                
                <table>
                    <thead>
                        <tr>
                            <th>العائد الصافي</th>
                            <th>المثل</th>
                            <th>التوقيت اللحظي</th>
                            <th>رقم الصفقة</th>
                        </tr>
                    </thead>
                    <tbody>
                        """
        
        if not captured_opportunities:
            html += """
                        <tr>
                            <td colspan="4" style="color: #666; padding: 15px;">جاري تشغيل خيوط الاتصال ومسح الـ 15 عملة الساخنة...</td>
                        </tr>
            """
        else:
            for opp in captured_opportunities:
                html += f"""
                        <tr>
                            <td style="color:#00ff88; font-weight:bold;">{opp['profit']}</td>
                            <td style="color:#fff; font-weight:bold;">{opp['pair']}</td>
                            <td style="color:#00e1ff;">{opp['time']}</td>
                            <td style="color:#888;">{opp['id']}</td>
                        </tr>
                """
                
        html += f"""
                    </tbody>
                </table>
                
                <p class="footer-text">15 HOT PAIRS FILTER ACTIVE • MILLISECONDS TIMING</p>
            </div>
        </body>
        </html>
        """
        self.wfile.write(html.encode('utf-8'))

def run_server():
    port = int(os.environ.get("PORT", 8080))
    server_address = ('', port)
    httpd = HTTPServer(server_address, SimpleWeb)
    print(f"[-] خادم لوحة التحكم HFT يعمل الآن على المنفذ: {port}")
    httpd.serve_forever()

if __name__ == "__main__":
    # 1. استدعاء خيط محرك المحاكاة أولاً
    t = threading.Thread(target=hft_simulation_engine)
    t.daemon = True
    t.start()
    
    # 2. استدعاء السيرفر للبدء الفوري (تمت إضافتها للتفعيل)
    run_server()
