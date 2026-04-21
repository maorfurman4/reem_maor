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
    return "CTO Bot is online and synced with Gemini 2.5!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# ─── AI Engine (Based on your working code) ────────────────────────────────
def get_gemini_feedback(text):
    # הפרומפט המקצועי שלך
    prompt = f"""
You are an elite Startup Architect and CTO Advisor operating inside a developer group chat.
Your task is to analyze raw startup ideas presented by the users and provide a structured, highly analytical, and realistic breakdown.

CRITICAL RULES:
1. NO PREAMBLE: Start directly with the analysis. No preamble.
2. LANGUAGE: Respond strictly in Hebrew, using precise professional and technical terminology.
3. FORMATTING: Use Markdown. Use the exact structure below.

---
### [כותרת קצרה הממצה את הרעיון] ###

1. 🔍 **סטטוס בשוק (האם קיים כבר?):**
   - מתחרים ישירים ועקיפים בולטים בשוק הישראלי והעולמי.
   - יתרון יחסי (Unfair Advantage).

2. 🧠 **סיבוכיות פיתוח ומורכבות (1-10):**
   - דירוג והסבר טכני קצר על האתגרים.

3. 🎯 **קהל יעד (Target Audience):**
   - הגדרה מדויקת של ה-Early Adopters.

4. 💰 **הערכת עלויות (Bootstrap / חודשי):**
   - הערכת עלויות שוטפות להרצת ה-MVP.

5. 🛠️ **סביבת פיתוח מומלצת (Tech Stack):**
   - Frontend, Backend, Database, AI.

6. 👥 **צוות ננדרש (Team Size):**
   - תפקידים הכרחיים ל-MVP.

7. ⏳ **משך זמן פיתוח (Time to MVP):**
   - הערכת לו"ז ריאלית.

8. 📋 **פירוק למשימות (Task Breakdown):**
   - שלב 1: מחקר ותשתיות.
   - שלב 2: Backend ו-API.
   - שלב 3: Frontend.
   - שלב 4: בדיקות והשקה.

---
הרעיון לניתוח:
"{text}"
    """

    # ה-URL המדויק מהקוד שעבד לך (כולל v1beta ו-2.5 flash)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY.strip()}"
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.2, # קצת יותר יצירתי לסטארטאפים
            "topP": 0.8,
            "topK": 40
        }
    }
    
    try:
        res = requests.post(url, json=payload, timeout=30)
        if res.status_code != 200:
            print(f"Gemini API Error: {res.status_code} - {res.text}")
            return f"שגיאה טכנית מול ג'מיני (קוד {res.status_code}). נסה שוב בעוד רגע."

        result_data = res.json()
        return result_data['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"שגיאה בחיבור למוח: {str(e)}"

# ─── Telegram Handlers ──────────────────────────────────────────────────────
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if str(message.chat.id) == str(GROUP_ID):
        if message.text and len(message.text) > 15:
            bot.send_chat_action(message.chat.id, 'typing')
            feedback = get_gemini_feedback(message.text)
            bot.reply_to(message, feedback)

# ─── Main Execution ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    Thread(target=run_flask).start()
    
    print("🚀 CTO Bot is starting (Gemini 2.5 Mode)...")
    
    while True:
        try:
            bot.polling(non_stop=True, timeout=15, skip_pending=True)
        except Exception as e:
            print(f"Telegram Conflict/Error: {e}. Sleeping 10s...")
            time.sleep(10)
