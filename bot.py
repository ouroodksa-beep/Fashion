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

# كود العمولة الخاص بكِ ليتم إلحاقه تلقائياً بكل الروابط
MY_AFFILIATE_PARAM = "ismg_ol=Dg3DA5Crnv1_01_KOC-C"

bot = telebot.TeleBot(TOKEN)


def generate_caption_with_ai(product_title):
    if not GEMINI_API_KEY:
        return "قطعة تجننن وتفتح النفس! شوفوا التفاصيل بالرابط ✨💕"

    prompt = f"""
أنتِ خبيرة تسويق وإعلانات لقناة تليجرام أنثوية مهتمة بالموضة والمنتجات.
قم بقراءة عنوان المنتج التالي المأخوذ من موقع التسوق، وتعرف على نوعه بدقة:

عنوان المنتج: "{product_title}"

المطلوب:
1. اكتب منشورًا قصيرًا وجذابًا جدًا بالعامية السعودية/الخليجية العصرية بنفس أسلوب قنوات التليجرام.
2. اكتب النص التسويقي المباشر بدون مقدمات أو شرح أو أسعار.
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


def attach_affiliate_code(url):
    """
    دمج كود التتبع الخاص بكِ بالرابط النهائي لضمان احتساب العمولة
    """
    if "ismg_ol=" in url:
        return url
    
    separator = "&" if "?" in url else "?"
    return f"{url}{separator}{MY_AFFILIATE_PARAM}"


def get_shein_product(raw_url):
    """
    قراءة المنتج عبر ScraperAPI من الرابط المباشر
    """
    api_url = f"http://api.scraperapi.com?api_key={SCRAPERAPI_KEY}&url={requests.utils.quote(raw_url)}"

    try:
        r = requests.get(api_url, timeout=30)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            title = None
            image = None

            og_title = soup.select_one('meta[property="og:title"]') or soup.select_one('meta[name="twitter:title"]')
            if og_title and og_title.get("content"):
                title = og_title["content"].strip()

            og_image = soup.select_one('meta[property="og:image"]') or soup.select_one('meta[name="twitter:image"]')
            if og_image and og_image.get("content"):
                image = og_image["content"].strip()

            if title:
                title = re.sub(r"\s*\|\s*SHEIN.*$", "", title, flags=re.IGNORECASE).strip()

            if image and image.startswith("//"):
                image = "https:" + image

            if title:
                return {"full_title": title, "image": image}
    except Exception as e:
        print(f"Scraper Error: {e}")

    return None


@bot.message_handler(func=lambda m: True)
def handler(msg):
    text = msg.text.strip()
    urls = re.findall(r"https?://\S+", text)

    if not urls:
        bot.reply_to(msg, "❌ يرجى إرسال رابط المنتج (سواء رابط عادي أو رابط أفيلييت)")
        return

    for original_url in urls:
        wait = bot.reply_to(msg, "⏳ جاري تحليل القطعة وتجهيز رابط العمولة الخاص بكِ...")

        # 1. محاولة قراءة بيانات المنتج
        product = get_shein_product(original_url)

        if not product or not product.get("full_title"):
            bot.edit_message_text("❌ لم نتمكن من قراءة العنوان تلقائياً من رابط onelink. يرجى إرسال رابط المنتج المباشر من المتصفح وسيقوم البوت بتحويله لرابط أفيلييت خاص بكِ تلقائياً.", msg.chat.id, wait.message_id)
            continue

        # 2. إنشاء رابط العمولة المضمون
        affiliate_link = attach_affiliate_code(original_url)
        
        # 3. صياغة النص بالذكاء الاصطناعي
        ai_caption = generate_caption_with_ai(product["full_title"])
        post = f"{ai_caption}\n\n🔗 {affiliate_link}"

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
