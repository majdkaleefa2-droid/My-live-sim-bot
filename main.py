import os
import asyncio
import random
from flask import Flask, render_template_string

app = Flask(__name__)

# =========================================================================
# 1. محرك البيانات المالي المطور المطابق كلياً للحساب الحقيقي (1,000$)
# =========================================================================
class TestnetLiveMirror1K:
    def __init__(self):
        # هوية المحاكاة المطابقة للحساب الحقيقي بالمليمتر
        self.status = "🛡️ HFT V6 PRO - وضع محاكاة الحساب الحقيقي (1K)"
        self.assets_count = 15
        
        # إعادة ضبط رأس المال والأمان ليتناسب مع 1,000 دولار
        self.initial_capital = 1000.0
        self.capital = 1000.0              
        self.net_profit = 0.0              
        
        # تصفير العدادات لبدء المراقبة الإحصائية النظيفة من الصفر
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        
        self.total_win_amount = 0.0       
        self.total_loss_amount = 0.0      
        
        self.last_snipe = "في انتظار ضربة جرس الافتتاح الأمريكي..."
        
        # هندسة الملاحقة الديناميكية المحددة بـ 10 دولارات (1% من الحساب)
        self.trailing_distance = 10.0
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

    def update_market_trade(self, is_win, gross_amount):
        if self.bot_stopped_by_trailing:
            return

        self.total_trades += 1
        
        # احتساب عمولة بينانس الفعالة المخصومة من عملة BNB (0.075%)
        fee = gross_amount * 0.00075

        if is_win:
            net_win = gross_amount - fee
            self.winning_trades += 1
            self.total_win_amount += net_win
            self.net_profit += net_win
            self.capital += net_win
            
            # رفع خط قفل الأرباح تلقائياً خلف القمة المحققة للمحفظة
            if self.capital > self.highest_equity:
                self.highest_equity = self.capital
                self.trailing_stop_level = self.highest_equity - self.trailing_distance
        else:
            # إضافة الرسوم فوق الخسارة لحساب التراجع الصافي بدقة
            total_loss_deducted = gross_amount + fee
            self.losing_trades += 1
            self.total_loss_amount += total_loss_deducted
            self.net_profit -= total_loss_deducted
            self.capital -= total_loss_deducted

        # قفل الحساب التراكمي وحجز الأرباح فور ملامسة خط الأمان المتحرك
        if self.capital <= self.trailing_stop_level and self.highest_equity > self.initial_capital:
            self.status = "🔒 PROFITS LOCKED (Trailing Stop Hit)"
            self.bot_stopped_by_trailing = True

radar = TestnetLiveMirror1K()

# =========================================================================
# 2. واجهة الرادار المحدثة (التحديث التلقائي الفوري كل ثانيتين)
# =========================================================================
RADAR_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>رادار السيولة - مرآة الحساب الحقيقي</title>
    <style>
        body { background-color: #0b0e11; color: #ffffff; font-family: Arial, sans-serif; padding: 15px; text-align: right; }
        .container { max-width: 480px; margin: auto; border: 2px solid #ffc107; padding: 20px; border-radius: 12px; background-color: #151a21; box-shadow: 0px 4px 15px rgba(0,0,0,0.5); }
        .header { font-size: 15px; font-weight: bold; margin-bottom: 15px; border-bottom: 1px solid #2d333b; padding-bottom: 10px; text-align: center; }
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
        <div class="header" style="color: {{ '#ff4444' if radar.bot_stopped_by_trailing else '#00ff66' }}">
            {{ radar.status }}
        </div>
        
        <div class="row">
            <span class="label">📊 رأس المال الموازي الحالي:</span>
            <span class="value">{{ "%.2f"|format(radar.capital) }} USDT</span>
        </div>
        
        <div class="row">
            <span class="label">📈 صافي الأرباح (بعد خصم العمولات):</span>
            <span class="value profit">{{ "+%.4f"|format(radar.net_profit) if radar.net_profit >= 0 else "%.4f"|format(radar.net_profit) }} USDT</span>
        </div>

        <!-- مربع الملاحقة الديناميكية لـ 1,000$ (مسافة 10$) -->
        <div class="box trailing-box">
            <div class="row" style="margin: 3px 0;">
                <span class="label">🔝 أعلى قمة وصل لها الحساب (1K):</span>
                <span class="value" style="color: #00ff66;">{{ "%.2f"|format(radar.highest_equity) }} USDT</span>
            </div>
            <div class="row" style="margin: 3px 0;">
                <span class="label">🛡️ خط حجز الأرباح (متحرك 10$):</span>
                <span class="value" style="color: #ffaa00;">{{ "%.2f"|format(radar.trailing_stop_level) }} USDT</span>
            </div>
        </div>

        <div class="box stats-box">
            <div class="row">
                <span>✅ صفقات ناجحة (Win): <b class="profit">{{ radar.winning_trades }}</b></span>
                <span>❌ صفقات عاكسة (Loss): <b class="loss">{{ radar.losing_trades }}</b></span>
            </div>
            <div class="row" style="margin-top: 5px;">
                <span>🎯 نسبة نجاح الرادار الحالية: <b style="color: #ffc107;">{{ metrics.win_rate }}%</b></span>
            </div>
        </div>

        <div class="box financial-box">
            <div class="row">
                <span class="label">💰 صافي متوسط ربح القنصة:</span>
                <span class="value profit">+{{"%.4f"|format(metrics.avg_win)}} USDT</span>
            </div>
            <div class="row">
                <span class="label">📉 صافي متوسط خسارة العاكسة:</span>
                <span class="value loss">-{{"%.4f"|format(metrics.avg_loss)}} USDT</span>
            </div>
            <div class="row" style="border-top: 1px solid #2d333b; padding-top: 5px; margin-top: 5px;">
                <span class="label">⚖️ عامل الربحية التراكمي (Profit Factor):</span>
                <span class="value" style="color: #58a6ff;">{{ metrics.profit_factor }}</span>
            </div>
        </div>
        
        <div class="shield">
            🛡️ آخر إشارة مرصودة: <span style="color: #ffc107;">{{ radar.last_snipe }}</span>
        </div>
    </div>
    
    <script>
        // تحديث تلقائي فائق السرعة كل ثانيتين لمواكبة افتتاح نيويورك العنيف
        setTimeout(function(){ location.reload(); }, 2000);
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    metrics = radar.get_metrics()
    return render_template_string(RADAR_TEMPLATE, radar=radar, metrics=metrics)

# =========================================================================
# 3. محرك المحاكاة الخلفي لـ 1,000$ (تضييق الخسارة الصارم STOP_0.12%)
# =========================================================================
async def live_trading_simulation():
    while True:
        await asyncio.sleep(random.randint(4, 8))
        if radar.bot_stopped_by_trailing:
            continue
            
        is_win = random.choices([True, False], weights=[0.96, 0.04])
        
        if is_win:
            actual_win = random.uniform(0.18, 0.28) 
            radar.update_market_trade(is_win=True, amount=actual_win)
        else:
            # 🎯 تضييق جدار وقف الخسارة الصارم (STOP_0.12% كحد أقصى لحساب الـ 1K)
            actual_loss = random.uniform(0.8, 1.2) 
            radar.update_market_trade(is_win=False, amount=actual_loss)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    loop = asyncio.get_event_loop()
    loop.create_task(live_trading_simulation())
    app.run(host='0.0.0.0', port=port)
