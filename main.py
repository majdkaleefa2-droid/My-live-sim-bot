# TOKEN: HFT_V7_PULSE_RIDER_PRO_SHIELD_OCT_6
# المحرك المتكامل والمطور - نسخة المضارب الخبير والمبرمج لـ 30 سنة (Python Version)

import time
import math

# 1. الإعدادات المتطورة وصمامات الأمان الصارمة
BotConfig = {
    "token": "HFT_V7_PULSE_RIDER_PRO_SHIELD_OCT_6",
    "environment": "live-sim",
    "baseUrl": "https://railway.app",
    "baseCapital": 200.00,  # USDT

    # إدارة المخاطر لحماية الـ 200 دولار
    "riskManagement": {
        "drawdownProtection": True,
        "maxDrawdownPercent": 5,   # صمام التراجع 5%
        "stopLossLimit": 10.0      # أقصى خسارة مسموحة 10 USDT
    },

    # فلاتر السوق والرادار القديم المطور
    "marketFilters": {
        "instantVolatilityWall": 1.00,  # جدار السيولة الصارم لمنع الصفقات الوهمية
        "maxAllowedPing": 250,         # تحمل الـ Ping مؤقتا لحين تعديل الـ Region
        "pulseSensitivity": 0.015      # حساسية رصد النبضات الحادة (1.5%)
    },

    # استراتيجية الخروج المقترحة من الخبير واقتناص القمم
    "profitTargetStrategy": {
        "takeProfit": {
            "enabled": True,
            "fixedTargetPercent": 0.018  # هدف جني أرباح خاطف وآمن عند 1.8%
        },
        "trailingProfit": {
            "active": True,
            "activationThreshold": 0.012,  # تفعيل ملاحقة الأرباح بعد صعود 1.2%
            "trailingStep": 0.004           # مسافة ملاحقة ضيقة (0.4%) لاقتناص القمة بدقة
        }
    }
}

# 2. حالة البوت الداخلية (State Management)
botState = {
    "currentBalance": BotConfig["baseCapital"],
    "totalWaves": 0,
    "successfulTrades": 0,
    "totalProfit": 0.0,
    "isPositionOpen": False,
    "entryPrice": 0.0,
    "currentPing": 215.2,
    "rollingStatus": "READY"
}

def fetchMarketData():
    # دالة محاكاة جلب البيانات اللحظية (تستبدل بـ API المنصة الحقيقي)
    return {
        "currentPrice": 1.00,
        "volatilityWall": 1.02,  # محاكاة اختراق الجدار 1.00x
        "pulseDelta": 0.016,     # محاكاة نبضة صاعدة بنسبة 1.6%
        "ping": 215.2
    }

def executeBuyOrder(price):
    botState["isPositionOpen"] = True
    botState["entryPrice"] = price
    botState["totalWaves"] += 1
    print(f"[TRADE OPEN] تم دخول صفقة شراء خاطفة بسعر: {price} USDT")

def closePosition(price, change, reason):
    profitAmount = botState["currentBalance"] * change
    botState["totalProfit"] += profitAmount
    botState["currentBalance"] += profitAmount
    botState["isPositionOpen"] = False
    
    if profitAmount > 0:
        botState["successfulTrades"] += 1
    
    print(f"[TRADE CLOSED] تم إغلاق الصفقة بناء على ({reason}) بربح: {profitAmount:.4f} USDT")

def manageOpenPosition(currentPrice):
    priceChangePercent = (currentPrice - botState["entryPrice"]) / botState["entryPrice"]

    # الخروج عند هدف جني الأرباح الثابت والمخطط له
    if priceChangePercent >= BotConfig["profitTargetStrategy"]["takeProfit"]["fixedTargetPercent"]:
        closePosition(currentPrice, priceChangePercent, "Take Profit")
    # صمام حماية الصفقة اللحظي في حال انعكس النبض
    elif priceChangePercent <= -0.01:
        closePosition(currentPrice, priceChangePercent, "Stop Loss")

def runMarketRadar():
    print(f"[RADAR] الرادار نشط ويراقب التوكن: {BotConfig['token']}")
    
    while True:
        try:
            marketData = fetchMarketData()
            botState["currentPing"] = marketData["ping"]
            
            # شرط الأمان الأول: التحقق من صمام التراجع
            if botState["totalProfit"] <= -BotConfig["riskManagement"]["stopLossLimit"]:
                botState["rollingStatus"] = "STOPPED (Drawdown Triggered)"
                print("[CRITICAL] تم تفعيل صمام التراجع! إيقاف البوت لحماية رأس المال.")
                break

            # رادار السيولة: هل اخترق السوق جدار السيولة اللحظي؟
            if marketData["volatilityWall"] >= BotConfig["marketFilters"]["instantVolatilityWall"]:
                
                # رادر النبضات
                if not botState["isPositionOpen"] and marketData["pulseDelta"] >= BotConfig["marketFilters"]["pulseSensitivity"]:
                    
                    # فحص سرعة الشبكة قبل التنفيذ
                    if botState["currentPing"] <= BotConfig["marketFilters"]["maxAllowedPing"]:
                        executeBuyOrder(marketData["currentPrice"])
                    else:
                        print(f"[SKIP] تم تجاهل النبضة لأن الـ Ping مرتفع جدا ({botState['currentPing']}ms).")
            
            # إدارة الصفقة المفتوحة
            if botState["isPositionOpen"]:
                manageOpenPosition(marketData["currentPrice"])

            time.sleep(0.1)  # يفحص السوق كل 100 ملي ثانية (HFT)

        except Exception as e:
            print(f"[ERROR] خطأ في رصد الرادار اللحظي: {str(e)}")
            time.sleep(1)

if __name__ == "__main__":
    runMarketRadar()
