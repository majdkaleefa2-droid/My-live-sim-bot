import os
import asyncio
import random
from flask import Flask, render_template_string

app = Flask(__name__)

# ==========================================
# 1. محرك البيانات المالي المطور (تضييق الخسائر الصارم)
# ==========================================
class AdvancedTradingRadar:
    def __init__(self):
        # البيانات الحية التراكمية
        self.status = "HFT V6 Active (Tight Risk Mode)"
        self.assets_count = 15
        self.initial_capital = 10000.0
        self.capital = 10026.25
        self.net_profit = 26.2510
        self.total_trades = 480
        self.winning_trades = 462
        self.losing_trades = 18
        
        # الأموال التراكمية بالدولار
        self.total_win_amount = 88.50   
        self.total_loss_amount = 62.25  
        
        self.last_snipe = "SHIBUSDT منذ 5.95 ثانية"
        
        # إعدادات الملاحقة الديناميكية وحجم المخاطرة الصارم
        self.trailing_distance = 50.0
        self.highest_equity = self.capital  
        self.trailing_stop_level = self.highest_equity - self.trailing_distance
        self.bot_stopped_by_trailing = False

    def get_metrics(self):
        avg_win = self.total_win_amount / self.winning_trades if self.winning_trades > 0 else 0
        avg_loss = self.total_loss_amount / self.losing_trades if self.losing_trades > 0 else 0
        win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0
        profit_factor = self.total_win_amount / self.total_loss_amount if self.total_loss_amount > 0 else self.total_win_amount
        
        return {
            "avg_win": round(avg_win, 4),
            "avg_loss": round(avg_loss, 4),
            "win_rate": round(win_rate, 2),
            "profit_factor": round(profit_factor, 2)
        }

    def update_market_trade(self, is_win, amount):
        if self.bot_stopped_by_trailing:
            return

        self.total_trades += 1
        if is_win:
            self.winning_trades += 1
            self.total_win_amount += amount
            self.net_profit += amount
            self.capital += amount
            
            if self.capital > self.highest_equity:
                self.highest_equity = self.capital
                self.trailing_stop_level = self.highest_equity - self.trailing_distance
        else:
            self.losing_trades += 1
            self.total_loss_amount += amount
            self.net_profit -= amount
            self.capital -= amount

        # تفعيل الخروج التلقائي لحماية الأرباح
        if self.capital <= self.trailing_stop_level and self.highest_equity > self.initial_capital:
            self.status = "🔒 PROFITS LOCKED (Trailing Stop Hit)"
            self.bot_stopped_by_trailing = True

# تفعيل كائن الرادار
radar = AdvancedTradingRadar()

# ==========================================
# 2. واجهة الرادار الشاملة والمطورة بالكامل
# ==========================================
RADAR_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>رادار السيولة الاحترافي - وضع تقليص المخاطر</title>
    <style>
        body { background-color: #0b0e11; color: #ffffff; font-family: Arial, sans-serif; padding: 15px; text-align: right; }
        .container { max-width: 480px; margin: auto; border: 2px solid #ffc107; padding: 20px; border-radius: 12px; background-color: #151a21; }
        .header { color: #00ff66; font-size: 16px; font-weight: bold; margin-bottom: 15px; border-bottom: 1px solid #2d333b; padding-bottom: 10px; text-align: center; }
        .row { display: flex; justify-content: space-between; margin: 10px 0; font-size: 15px; }
        .label { color: #8b949e; }
        .value { font-weight: bold; color: #58a6ff; }
        .profit { color: #00ff66; }
        .loss { color: #ff4444; }
        .box { padding: 10px 12px; border-radius: 8px; margin: 10px 0; font-size: 14px; }
        .stats-box { background-color: #1c2128; border-right: 4px solid #ffc107; }
        .financial-box { background-color: #17223b; border-right: 4px solid #58a6ff; }
        .trailing-box { background-color: #24221c; border-right: 4px solid #ffaa00; }
        .shield { color: #ffc107; border-top: 1px solid #2d333b; padding-top: 10px; margin-top: 15px; font-size: 13px; text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header" style="color: #00ff66;">
            🛡️ {{ radar.status }}
        </div>
        
        <div class="row">
            <span class="label">📊 رأس المال الحالي الحقيقي:</span>
            <span class="value">{{ "%.2f"|format(radar.capital) }} USDT</span>
        </div>
        
        <div class="row">
            <span class="label">📈 صافي الأرباح المحققة:</span>
            <span class="value profit">{{ "+%.4f"|format(radar.net_profit) if radar.net_profit >= 0 else "%.4f"|format(radar.net_profit) }} USDT</span>
        </div>

        <!-- مربع الملاحقة الديناميكية (50$) -->
        <div class="box trailing-box">
            <div class="row" style="margin: 3px 0;">
                <span class="label">🔝 أعلى قمة للمحفظة:</span>
                <span class="value" style="color: #00ff66;">{{ "%.2f"|format(radar.highest_equity) }} USDT</span>
            </div>
            <div class="row" style="margin: 3px 0;">
                <span class="label">🛡️ خط قفل الأرباح (متحرك):</span>
                <span class="value" style="color: #ffaa00;">{{ "%.2f"|format(radar.trailing_stop_level) }} USDT</span>
            </div>
        </div>

        <div class="box stats-box">
            <div class="row">
                <span>✅ صفقات ناجحة (Win): <b class="profit">{{ radar.winning_trades }}</b></span>
                <span>❌ صفقات عاكسة (Loss): <b class="loss">{{ radar.losing_trades }}</b></span>
            </div>
            <div class="row" style="margin-top: 5px;">
                <span>🎯 نسبة نجاح الاستراتيجية: <b style="color: #ffc107;">{{ metrics.win_rate }}%</b></span>
            </div>
        </div>

        <!-- المربع المالي المحدث ليعكس تضييق حجم الخسارة العاكسة -->
        <div class="box financial-box">
            <div class="row">
                <span class="label">💰 متوسط ربح الصفقة الناجحة:</span>
                <span class="value profit">+{{"%.4f"|format(metrics.avg_win)}} USDT</span>
            </div>
            <div class="row">
                <span class="label">📉 متوسط خسارة الصفقة العاكسة:</span>
                <span class="value loss">-{{"%.4f"|format(metrics.avg_loss)}} USDT</span>
            </div>
            <div class="row" style="border-top: 1px solid #2d333b; padding-top: 5px; margin-top: 5px;">
                <span class="label">⚖️ عامل الربحية العام (Profit Factor):</span>
                <span class="value" style="color: #58a6ff;">{{ metrics.profit_factor }}</span>
            </div>
        </div>
        
        <div class="shield">
            🛡️ آخر قنص تمت فلترته: <span style="color: #ffc107;">{{ radar.last_snipe }}</span>
        </div>
    </div>
    
    <script>
        setTimeout(function(){ location.reload(); }, 3000);
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    metrics = radar.get_metrics()
    return render_template_string(RADAR_TEMPLATE, radar=radar, metrics=metrics)

# ==========================================
# 3. محاكي المحرك الخلفي المطور بتعديل المخاطرة الصارم
# ==========================================
async def live_trading_simulation():
    while True:
        await asyncio.sleep(random.randint(4, 8))
        if radar.bot_stopped_by_trailing:
            continue
            
        is_win = random.choices([True, False], weights=[0.96, 0.04])
        
        if is_win:
            actual_win = round(random.uniform(0.15, 0.25), 4) # ربح القنص السريع الافتراضي
            radar.update_market_trade(is_win=True, amount=actual_win)
        else:
            # 🎯 التطبيق العملي لتضييق الخسارة (STOP_0.15% كحد أقصى بدلاً من 3.4 دولار)
            actual_loss = round(random.uniform(0.9, 1.3), 4) 
            radar.update_market_trade(is_win=False, amount=actual_loss)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    loop = asyncio.get_event_loop()
    loop.create_task(live_trading_simulation())
    app.run(host='0.0.0.0', port=port)
