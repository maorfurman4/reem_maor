import os
import telebot
import requests
from flask import Flask
from threading import Thread

# טעינת הסודות
TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY_1")
GROUP_ID = os.environ.get("GROUP_ID")

bot = telebot.TeleBot(TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "CTO Bot is alive and listening!"

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
    try:
        res = requests.post(url, json=payload, timeout=25)
        res.raise_for_status() # בודק אם ה-API החזיר שגיאה
        return res.json()['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        # כאן התיקון - מדפיס את השגיאה ללוגים של Render
        print(f"--- GEMINI API ERROR ---")
        print(f"Error details: {e}")
        if 'res' in locals():
            print(f"Response body: {res.text}")
        return f"שגיאה טכנית בחיבור לג'מיני: {e}"

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if str(message.chat.id) == str(GROUP_ID):
        if message.text and len(message.text) > 15:
            bot.send_chat_action(message.chat.id, 'typing')
            feedback = get_gemini_feedback(message.text)
            bot.reply_to(message, feedback)

if __name__ == "__main__":
    Thread(target=run_flask).start()
    print("🚀 CTO Bot is online and fixed!")
    bot.infinity_polling()
