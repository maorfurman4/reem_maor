import os
import time
import telebot
import requests
from flask import Flask
from threading import Thread

# טעינת הסודות + ניקוי אוטומטי של רווחים נסתרים
TOKEN = os.environ.get("TELEGRAM_TOKEN", "").strip()
GEMINI_KEY = os.environ.get("GEMINI_API_KEY_1", "").strip()
GROUP_ID = os.environ.get("GROUP_ID", "").strip()

bot = telebot.TeleBot(TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "CTO Bot is active, upgraded to Gemini 2.0, and listening!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def get_gemini_feedback(text):
    if not GEMINI_KEY:
        return "שגיאה: חסר מפתח API של ג'מיני."

    # שדרוג למודל 2.0 החדש
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}"
    
    prompt = f"""
You are an elite Startup Architect and CTO Advisor operating inside a developer group chat.
Your task is to analyze raw startup ideas presented by the users and provide a structured, highly analytical, and realistic breakdown.

CRITICAL RULES:
1. NO PREAMBLE: Start directly with the analysis. Directly to the content. No preamble. Do not say "Here is the analysis" or "That's a great idea".
2. LANGUAGE: Respond strictly in Hebrew, using precise professional and technical terminology.
3. FORMATTING: Use Markdown. Use the exact structure below. If a parameter is unknown, state your best logical assumption.

---
### [כותרת קצרה הממצה את הרעיון] ###

1. 🔍 **סטטוס בשוק (האם קיים כבר?):**
   - מתחרים ישירים ועקיפים בולטים בשוק הישראלי והעולמי.
   - יתרון יחסי (Unfair Advantage) - מה אנחנו צריכים לעשות אחרת כדי לנצח?

2. 🧠 **סיבוכיות פיתוח ומורכבות (1 קל עד 10 קשה מאוד):**
   - דירוג הסיבוכיות.
   - הסבר טכני קצר על האתגרים המרכזיים (למשל: סנכרון זמן אמת, עבודה עם חומרה, רגולציה).

3. 🎯 **קהל יעד (Target Audience):**
   - הגדרה מדויקת של ה-Early Adopters. למי זה פותר כאב אמיתי?

4. 💰 **הערכת עלויות (Bootstrap / חודשי):**
   - הערכת עלויות שוטפות להרצת ה-MVP (שרתים ב-Render/AWS, שירותי צד שלישי, API, אוטומציות).

5. 🛠️ **סביבת פיתוח מומלצת (Tech Stack):**
   - Frontend, Backend, Database, שירותי AI ענן מומלצים לפרויקט הספציפי הזה.

6. 👥 **צוות נדרש (Team Size):**
   - אילו תפקידים הכרחיים כדי להרים MVP (למשל: 1 Fullstack, 1 איש UI/UX).

7. ⏳ **משך זמן פיתוח (Time to MVP):**
   - הערכת לו"ז ריאלית בחודשים או שבועות.

8. 📋 **פירוק למשימות (Task Breakdown):**
   - שלב 1: מחקר, אפיון ותשתיות.
   - שלב 2: פיתוח Backend ו-API.
   - שלב 3: פיתוח Frontend / אפליקציה.
   - שלב 4: בדיקות, QA והשקה.

---
הנה הרעיון שעליך לנתח:
"{text}"
    """
    
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    headers = {'Content-Type': 'application/json'}
    
    try:
        res = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if res.status_code != 200:
            print(f"Gemini API Error: {res.status_code} - {res.text}")
            return f"שגיאת API מג'מיני (קוד {res.status_code})."

        data = res.json()
        
        if 'candidates' in data and len(data['candidates']) > 0:
            candidate = data['candidates'][0]
            if 'content' in candidate and 'parts' in candidate['content']:
                return candidate['content']['parts'][0]['text']
            elif 'finishReason' in candidate and candidate['finishReason'] == 'SAFETY':
                return "⚠️ הרעיון נחסם על ידי מנגנון הבטיחות של ג'מיני."
                
        return "ג'מיני החזיר תשובה ריקה. נסה שוב."

    except Exception as e:
        print(f"Code Error: {e}")
        return f"שגיאה טכנית בחיבור לשרתי AI: {e}"

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if str(message.chat.id) == str(GROUP_ID):
        if message.text and len(message.text) > 15:
            bot.send_chat_action(message.chat.id, 'typing')
            feedback = get_gemini_feedback(message.text)
            bot.reply_to(message, feedback)

if __name__ == "__main__":
    Thread(target=run_flask).start()
    
    print("🚀 CTO Bot is starting with Gemini 2.0 Flash!")
    
    # מנגנון האלמוות - מונע מהבוט לקרוס כשיש התנגשות עם טלגרם
    while True:
        try:
            print("🔄 מנסה להתחבר לטלגרם...")
            bot.polling(non_stop=True, timeout=10, long_polling_timeout=5)
        except Exception as e:
            print(f"⚠️ שגיאת חיבור לטלגרם (לרוב בגלל בוט כפול 409). ממתין 15 שניות ומנסה שוב... פרטים: {e}")
            time.sleep(15)
