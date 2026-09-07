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

bot = telebot.TeleBot(TOKEN)


def generate_caption_with_ai(product_title):
    if not GEMINI_API_KEY:
        return "قطعة مميزة وجذابة، التفاصيل بالرابط ✨"

    prompt = f"""
أنتِ خبيرة تسويق محترفة لقناة صيدات وعروض في التليجرام تسوق لمنتجات شي إن (SHEIN).
قم بقراءة عنوان المنتج التالي المأخوذ من الموقع، وتعرف على نوعه والجمهور المستهدف تلقائياً:

عنوان المنتج: "{product_title}"

المطلوب:
1. حلل نوع المنتج (نسائي/بناتي، رجالي، أطفال، أو مستلزمات منزلية).
2. اكتب منشوراً تسويقياً قصيراً ومؤثراً بالعامية السعودية/الخليجية وفقاً للأسلوب التالي:
   - إذا كان المنتج **نسائي أو بناتي**: استخدم أسلوباً راقياً، أنيقاً، وجذاباً يركز على الأناقة والتفاصيل (مثل: تجنن، كشخة، قماشها يفتح النفس، لطيفة باللبس).
   - إذا كان المنتج **رجالي**: استخدم أسلوباً مباشراً، عملياً، وموجهاً للرجال (مثل: فخمة ومريحة، مرتبة للإطلالة اليومية، خامة ممتازة).
   - إذا كان **أطفال أو مستلزمات**: استخدم أسلوباً لطيفاً ومحفزاً للأمهات.
3. لا تكتب أي مقدمات أو شرح، ولا تذكر الأسعار أو الكود، اكتب النص التسويقي النهائي مباشرة مع إيموجيز مناسبة للقطعة.
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


def get_shein_product(raw_url):
    """
    استخراج بيانات القطعة عبر محاكاة متصفح الموبايل الحقيقي وتتبع التوجيه المباشر
    """
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ar-SA,ar;q=0.9",
    }

    try:
        # 1. تتبع رابط onelink للوصول إلى الصفحة النهائية
        res = session.get(raw_url, headers=headers, allow_redirects=True, timeout=15)
        soup = BeautifulSoup(res.text, "html.parser")

        title = None
        image = None

        # 2. البحث عن العنوان في وسوم OG و HTML
        for selector in ['meta[property="og:title"]', 'meta[name="twitter:title"]', 'title']:
            tag = soup.select_one(selector)
            if tag:
                content = tag.get("content") or tag.text
                if content and len(content.strip()) > 5:
                    title = content.strip()
                    break

        # 3. البحث عن الصورة
        for img_selector in ['meta[property="og:image"]', 'meta[name="twitter:image"]']:
            img_tag = soup.select_one(img_selector)
            if img_tag and img_tag.get("content"):
                image = img_tag["content"].strip()
                break

        if title:
            title = re.sub(r"\s*\|\s*SHEIN.*$", "", title, flags=re.IGNORECASE).strip()
            title = re.sub(r"^SHEIN\s*", "", title, flags=re.IGNORECASE).strip()

        if image and image.startswith("//"):
            image = "https:" + image

        if title and "SHEIN" not in title and len(title) > 3:
            return {"full_title": title, "image": image}

    except Exception as e:
        print(f"Extraction Error: {e}")

    return None


@bot.message_handler(func=lambda m: True)
def handler(msg):
    text = msg.text.strip()
    urls = re.findall(r"https?://\S+", text)

    if not urls:
        bot.reply_to(msg, "❌ يرجى إرسال رابط المنتج")
        return

    for original_url in urls:
        wait = bot.reply_to(msg, "⏳ جاري تحليل القطعة وصياغة المنشور...")

        # 1. جلب بيانات القطعة تلقائياً بدون تغيير الرابط
        product = get_shein_product(original_url)

        if not product or not product.get("full_title"):
            bot.edit_message_text(
                "❌ تعذر استخراج تفاصيل القطعة تلقائياً من شي إن بسبب قيود الحماية الحالية على رابط onelink.",
                msg.chat.id, 
                wait.message_id
            )
            continue

        # 2. صياغة النص بـ Gemini
        ai_caption = generate_caption_with_ai(product["full_title"])
        
        # 3. إرسال المنشور مع رابط الأفلييت كما هو
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
