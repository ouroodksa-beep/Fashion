import telebot
import re
import time
import requests
import json
from bs4 import BeautifulSoup
from flask import Flask, request


# =========================================================
# المفاتيح
# =========================================================

TOKEN = "8888709197:AAEVCTpVticEzi-NBaWRdIQDmKJSxdRzA54"

GEMINI_API_KEY = "AIzaSyAD68JzBWieLXb9kE-7qOg-8p10_EkY518"

# =========================================================
# Bot
# =========================================================

bot = telebot.TeleBot(TOKEN)


# =========================================================
# Gemini
# =========================================================

def generate_caption_with_ai(product_title):

    prompt = f"""
أنتِ خبيرة تسويق محترفة لقناة صيدات وعروض في التليجرام
تسوق لمنتجات شي إن (SHEIN).

عنوان المنتج:
"{product_title}"

المطلوب:

1. حللي نوع المنتج تلقائياً:
نسائي/بناتي، رجالي، أطفال، أو مستلزمات منزلية.

2. اكتبي منشوراً تسويقياً قصيراً ومؤثراً
بالعامية السعودية/الخليجية.

3. إذا كان المنتج نسائي أو بناتي:
استخدمي أسلوباً راقياً وأنيقاً وجذاباً
يركز على الأناقة والتفاصيل.
مثل:
تجنن، كشخة، قماشها يفتح النفس، لطيفة باللبس.

4. إذا كان المنتج رجالي:
استخدمي أسلوباً مباشراً وعملياً وفخماً.

5. إذا كان المنتج أطفال أو مستلزمات:
استخدمي أسلوباً لطيفاً ومحفزاً للأمهات.

6. استخدمي إيموجيز مناسبة للقطعة.

7. لا تذكري الأسعار.

8. لا تذكري الكود.

9. لا تكتبي أي مقدمات أو شرح.

10. لا تقولي إنك ذكاء اصطناعي.

أريد النص التسويقي النهائي فقط.
"""

    # -----------------------------------------------------
    # موديل Gemini
    # -----------------------------------------------------

    model = "gemini-1.5-flash"

    url = (
        "https://generativelanguage.googleapis.com/"
        f"v1beta/models/{model}:generateContent"
        f"?key={GEMINI_API_KEY}"
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.8,
            "maxOutputTokens": 300
        }
    }

    try:

        print("======================================")
        print("🤖 جاري إرسال الطلب إلى Gemini")
        print("Model:", model)
        print("======================================")

        response = requests.post(
            url,
            json=payload,
            headers={
                "Content-Type": "application/json"
            },
            timeout=30
        )

        print(
            "Gemini Status:",
            response.status_code
        )

        # =================================================
