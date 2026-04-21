import os
import time
import telebot
import requests
from flask import Flask
from threading import Thread

# טעינת הסודות מ-Render
TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY_1")
GROUP_ID = os.environ.get("GROUP_ID")

bot = telebot.TeleBot(TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "CTO Bot is active and running smoothly!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def get_gemini_feedback(text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    
    prompt = f"""
You are an elite Startup Architect and CTO Advisor operating inside a developer group chat.
Your task is to analyze raw startup ideas presented by the users and provide a structured, highly analytical, and realistic breakdown.

CRITICAL RULES:
1. NO PREAMBLE: Start directly with the analysis. Directly to the content. No preamble.
2. LANGUAGE: Respond strictly in Hebrew, using precise professional and technical terminology.
3. FORMATTING: Use Markdown.

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
            return "משהו השתבש בחיבור למוח של ה-CTO... נסו שוב בעוד רגע."
        return res.json()['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        print(f"Technical Error: {e}")
        return "שגיאה טכנית בחיבור. בדוק את הלוגים."

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    # מוודא שההודעה נשלחה בקבוצה שהגדרנו
    if str(message.chat.id) == str(GROUP_ID):
        if message.text and len(message.text) > 10:
            bot.send_chat_action(message.chat.id, 'typing')
            feedback = get_gemini_feedback(message.text)
            bot.reply_to(message, feedback)

if __name__ == "__main__":
    # מפעיל את השרת של Render ברקע
    Thread(target=run_flask).start()
    
    print("🚀 Waiting 8 seconds to clear old connections (Fix for 409 Conflict)...")
    time.sleep(8) # השהייה קריטית לפתרון שגיאת 409
    
    print("🚀 CTO Bot is starting to listen!")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
