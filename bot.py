import telebot
import re
import time
import os
import requests
import json
from bs4 import BeautifulSoup
from flask import Flask, request

# ─── التوكن ومفاتيح التشغيل ───
TOKEN = os.environ.get("BOT_TOKEN", "8888709197:AAEVCTpVticEzi-NBaWRdIQDmKJSxdRzA54")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyAD68JzBWieLXb9kE-7qOg-8p10_EkY518")
SCRAPERAPI_KEY = os.environ.get("SCRAPERAPI_KEY", "fb7742b2e62f3699d5059eea890268dd")

bot = telebot.TeleBot(TOKEN)


def generate_caption_with_ai(product_title):
    """
    إرسال عنوان المنتج لـ Gemini ليحلله بدقة ويكتب وصفًا أنثويًا جذابًا
    """
    if not GEMINI_API_KEY:
        return "قطعة تجننن وتفتح النفس! شوفوا التفاصيل بالرابط ✨💕"

    prompt = f"""
أنتِ خبيرة تسويق وإعلانات لقناة تليجرام أنثوية مهتمة بالموضة والمنتجات (مثل قناة مون فاشن).
قم بقراءة عنوان المنتج التالي المأخوذ من موقع التسوق، وتعرف على نوعه بدقة (هل هو ملابس، مج/كوب، مكياج، ديكور، مفرش، إكسسوار... إلخ) ولونه وخامته إن وجدت:

عنوان المنتج: "{product_title}"

المطلوب:
1. اكتب منشورًا قصيرًا وجذابًا جدًا بالعامية السعودية/الخليجية العصرية بنفس أسلوب قنوات التليجرام (استخدم كلمات حماسية مثل: مرررره، يجننن، خيالي، تخدمكم، رايقة، مع إموجيات مناسبة).
2. يجب أن يكون الكلام مطبقًا 100% على طبيعة المنتج (مثلاً: إذا كان مج أو كوب لا تتحدث عن اللبس بل عن القهوة والروقان، إذا كان مكياج تحدث عن النضارة والدمج، إذا كان فستان تحدث عن الكشخة والقصة).
3. اكتب النص التسويقي المباشر بدون مقدمات أو شرح أو أسعار.
4. اذكر التفاصيل (اللون/النوع/الخامة) بشكل دقيق بناءً على العنوان فقط بدون تأليف ألوان غير موجودة.

اكتب النص النهائي مباشرة بدون أي مقدمات أو شرح.
"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=15)
        if response.status_code == 200:
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text'].strip()
    except Exception as e:
        print(f"Gemini Exception: {e}")

    return "قطعة أنيقة وعصرية، شوفوا كامل التفاصيل في الرابط ✨"


def get_shein_product(url):
    """
    تجاوز حماية شي إن عبر ScraperAPI لاستخراج اسم المنتج وصورته
    """
    if not SCRAPERAPI_KEY:
        print("ScraperAPI key is missing!")
        return None

    # تحويل الطلب عبر ScraperAPI لتجاوز الحظر وتتبع التوجيه تلقائياً
    api_url = f"http://api.scraperapi.com?api_key={SCRAPERAPI_KEY}&url={requests.utils.quote(url)}&render=true"

    try:
        r = requests.get(api_url, timeout=35)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")

            title = None
            og_title = soup.select_one('meta[property="og:title"]')
            if og_title and og_title.get("content"):
                title = og_title["content"].strip()
            
            if not title:
                title_tag = soup.select_one("title")
                if title_tag:
                    title = title_tag.get_text(strip=True)
                    title = re.sub(r"\s*\|\s*SHEIN.*$", "", title, flags=re.IGNORECASE)

            image = None
            og_image = soup.select_one('meta[property="og:image"]')
            if og_image and og_image.get("content"):
                image = og_image["content"].strip()

            if image:
                if image.startswith("//"):
                    image = "https:" + image
                elif image.startswith("/"):
                    image = "https://www.shein.com" + image

            if title:
                return {"full_title": title, "image": image}

    except Exception as e:
        print(f"ScraperAPI Error: {e}")

    return None


@bot.message_handler(func=lambda m: True)
def handler(msg):
    text = msg.text.strip()
    urls = re.findall(r"https?://\S+", text)

    if not urls:
        bot.reply_to(msg, "❌ يرجى إرسال رابط المنتج")
        return

    for original_url in urls:
        wait = bot.reply_to(msg, "⏳ جاري قراءة المنتج وتحليله بالذكاء الاصطناعي...")

        product = get_shein_product(original_url)

        if not product or not product.get("full_title"):
            bot.edit_message_text("❌ تعذر قراءة عنوان المنتج، يرجى إعادة المحاولة.", msg.chat.id, wait.message_id)
            continue

        ai_caption = generate_caption_with_ai(product["full_title"])
        post = f"{ai_caption}\n\n🔗 {original_url}"

        try:
            if product.get("image"):
                bot.send_photo(msg.chat.id, product["image"], caption=post)
            else:
                bot.send_message(msg.chat.id, post)
            bot.delete_message(msg.chat.id, wait.message_id)
        except Exception as e:
            print(f"Error sending message: {e}")
            bot.edit_message_text("❌ حدث خطأ أثناء إرسال المنشور", msg.chat.id, wait.message_id)


# ─── Flask & Webhook Setup ───
app = Flask(__name__)

WEBHOOK_HOST = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
WEBHOOK_PORT = int(os.environ.get("PORT", 10000))
WEBHOOK_URL_BASE = f"https://{WEBHOOK_HOST}" if WEBHOOK_HOST else None
WEBHOOK_URL_PATH = f"/webhook/{TOKEN}"

@app.route("/")
def index():
    return "🤖 البوت يعمل بنجاح"

@app.route(WEBHOOK_URL_PATH, methods=["POST"])
def webhook():
    if request.headers.get("content-type") == "application/json":
        json_string = request.get_data().decode("utf-8")
        try:
            update_dict = json.loads(json_string)
            update = telebot.types.Update.de_json(update_dict)
            bot.process_new_updates([update])
            return "OK", 200
        except Exception as e:
            print(f"Webhook error: {e}")
            return "Bad Request", 400
    else:
        return "Unsupported Media Type", 415

def start_webhook():
    if WEBHOOK_HOST:
        bot.remove_webhook()
        time.sleep(0.5)
        bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH)

    app.run(host="0.0.0.0", port=WEBHOOK_PORT)

if __name__ == "__main__":
    start_webhook()
