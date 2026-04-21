import os
import time
import telebot
import requests
import json
from flask import Flask
from threading import Thread

# ─── Config ────────────────────────────────────────────────────────────────
TOKEN = os.environ.get("TELEGRAM_TOKEN", "").strip()
GEMINI_KEY = os.environ.get("GEMINI_API_KEY_1", "").strip()
GROUP_ID = os.environ.get("GROUP_ID", "").strip()

bot = telebot.TeleBot(TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "CTO Bot is online with Gemini 3 Flash!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# ─── AI Engine (Upgraded to Gemini 3 Flash for Stability) ──────────────────
def get_gemini_feedback(text):
    if not GEMINI_KEY:
        return "שגיאה: חסר מפתח API ב-Render."

    # שימוש במודל Gemini 3 Flash - הכי יציב וחזק ב-2026
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash:generateContent?key={GEMINI_KEY.strip()}"
    
    prompt = f"""
You are an elite Startup Architect and CTO Advisor operating inside a developer group chat.
Analyze this idea: "{text}"

CRITICAL RULES:
1. NO PREAMBLE: Start directly with the analysis.
2. LANGUAGE: Hebrew only.
3. FORMATTING: Use Markdown with the 8-point structure (Market, Complexity, Audience, Cost, Tech, Team, Time, Tasks).
    """

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 2048
        }
    }
    
    # מנגנון להתמודדות עם שגיאות 503 (ניסיון חוזר)
    for attempt in range(3):
        try:
            res = requests.post(url, json=payload, timeout=30)
            
            if res.status_code == 200:
                result_data = res.json()
                return result_data['candidates'][0]['content']['parts'][0]['text']
            
            if res.status_code == 503:
                print(f"⚠️ Google Server Busy (503). Attempt {attempt+1}/3. Waiting...")
                time.sleep(2) # מחכה 2 שניות ומנסה שוב
                continue
                
            return f"שגיאה מה-API (קוד {res.status_code}): {res.text[:100]}"
            
        except Exception as e:
            if attempt == 2: return f"שגיאת תקשורת: {str(e)}"
            time.sleep(1)
            
    return "השרת של גוגל עמוס מדי כרגע. נסה שוב בעוד כמה דקות."

# ─── Telegram Handlers ──────────────────────────────────────────────────────
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if str(message.chat.id) == str(GROUP_ID):
        if message.text and len(message.text) > 10:
            bot.send_chat_action(message.chat.id, 'typing')
            feedback = get_gemini_feedback(message.text)
            bot.reply_to(message, feedback)

# ─── Main Execution ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    Thread(target=run_flask).start()
    
    print("🚀 CTO Bot is starting (Gemini 3 Flash Mode)...")
    
    while True:
        try:
            bot.polling(non_stop=True, timeout=15, skip_pending=True)
        except Exception as e:
            # מטפל בשגיאת 409 ובשגיאות חיבור אחרות בלי לקרוס
            print(f"Connection issue: {e}. Retrying in 10s...")
            time.sleep(10)
