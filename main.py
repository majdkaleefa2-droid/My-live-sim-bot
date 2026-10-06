from fastapi.responses import HTMLResponse

@app.get("/radar", response_class=HTMLResponse)
def show_professional_radar():
    """واجهة الرادار الاحترافية الحية لنسخة HFT V7 - وضع الميكرو الصارم"""
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
                // تحديث تلقائي كل 2 ثانية لسحب البيانات الحية بدون تقسيط
                setTimeout(function(){{ location.reload(); }}, 2000);
            </script>
        </body>
    </html>
    """
    return html_content
