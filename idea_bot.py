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
    return "CTO Bot is Active"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# ─── AI Engine (זהה לחלוטין לקוד היומן שלך) ──────────────────
def get_gemini_feedback(text):
    # הפרומפט שלך
    prompt = f"""אתה עוזר אקדמי ומומחה CTO. נתח את הרעיון הבא בצורה מקצועית, בעברית, עם Markdown: "{text}" """

    # הכתובת והמודל שעבדו לך ביומן
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY.strip()}"
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.1
        }
    }
    
    try:
        res = requests.post(url, json=payload, timeout=30)
        if res.status_code != 200:
            return f"שגיאה {res.status_code}: {res.text[:100]}"
            
        result_data = res.json()
        return result_data['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"תקלה טכנית: {str(e)}"

# ─── Telegram Handler ──────────────────────────────────────────────────────
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if str(message.chat.id) == str(GROUP_ID):
        if message.text and len(message.text) > 10:
            bot.send_chat_action(message.chat.id, 'typing')
            feedback = get_gemini_feedback(message.text)
            bot.reply_to(message, feedback)

# ─── Main ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    Thread(target=run_flask).start()
    
    print("🚀 Bot starting with Gemini 2.5 Flash...")
    
    while True:
        try:
            # המתנה קצרה למנוע התנגשויות 409
            bot.polling(non_stop=True, timeout=20, skip_pending=True)
        except Exception as e:
            print(f"Error: {e}. Retrying...")
            time.sleep(10)
