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
    if not GEMINI_API_KEY:
        return "قطعة مميزة وجذابة، التفاصيل الكاملة بالرابط ✨"

    prompt = f"""
أنتِ خبيرة تسويق محترفة لقناة صيدات وعروض في التليجرام تسوق لمنتجات شي إن (SHEIN).
قم بقراءة عنوان المنتج التالي المأخوذ من الموقع، وتعرف على نوعه والجمهور المستهدف تلقائياً:

عنوان المنتج: "{product_title}"

المطلوب:
1. حلل نوع المنتج (نسائي/بناتي، رجالي، أطفال، أو مستلزمات منزلية).
2. اكتب منشوراً تسويقياً قصيراً ومؤثراً بالعامية السعودية/الخليجية وفقاً للأسلوب التالي:
   - إذا كان المنتج **نسائي أو بناتي**: استخدم أسلوباً راقياً، أنيقاً، وجذاباً يركز على الأناقة والتفاصيل (مثل: تجنن، كشخة، قماشها يفتح النفس، لطيفة باللبس).
   - إذا كان المنتج **رجالي**: استخدم أسلوباً مباشراً، عملياً، وموجهاً للرجال (مثل: فخمة ومريحة، مرتبة للإطلالة اليومية، خامة ممتازة، كشخة).
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

    return "قطعة مميزة وجذابة، شوفوا كامل التفاصيل في الرابط ✨"


def resolve_final_url(url):
    """
    تتبع رابط onelink للوصول إلى رابط شي إن النهائي المباشر
    """
    try:
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
        })
        res = session.head(url, allow_redirects=True, timeout=10)
        return res.url
    except Exception:
        return url


def get_shein_product(raw_url):
    """
    جلب عنوان المنتج وصورته بفك الروابط المختصرة واستخراج الميتا داتا بأكثر من وسيلة
    """
    # 1. تتبع التحويل للوصول للرابط الأصلي
    final_url = resolve_final_url(raw_url)
    
    # 2. قراءة الرابط عبر ScraperAPI
    api_url = f"http://api.scraperapi.com?api_key={SCRAPERAPI_KEY}&url={requests.utils.quote(final_url)}&render=true"

    try:
        r = requests.get(api_url, timeout=35)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            title = None
            image = None

            # محاولة جلب العنوان من الوسوم المختلفة
            og_title = (soup.select_one('meta[property="og:title"]') or 
                        soup.select_one('meta[name="twitter:title"]') or 
                        soup.select_one('title'))
            
            if og_title:
                title = og_title.get("content") or og_title.text

            # محاولة جلب الصورة
            og_image = soup.select_one('meta[property="og:image"]') or soup.select_one('meta[name="twitter:image"]')
            if og_image and og_image.get("content"):
                image = og_image["content"].strip()

            if title:
                # تنظيف العنوان من الكلمات الزائدة
                title = re.sub(r"\s*\|\s*SHEIN.*$", "", title, flags=re.IGNORECASE).strip()
                title = re.sub(r"SHEIN\s*", "", title, flags=re.IGNORECASE).strip()

            if image and image.startswith("//"):
                image = "https:" + image

            if title and len(title) > 3:
                return {"full_title": title, "image": image}
    except Exception as e:
        print(f"Scraper Error: {e}")

    return None


@bot.message_handler(func=lambda m: True)
def handler(msg):
    text = msg.text.strip()
    urls = re.findall(r"https?://\S+", text)

    if not urls:
        bot.reply_to(msg, "❌ يرجى إرسال رابط المنتج")
        return

    for original_url in urls:
        wait = bot.reply_to(msg, "⏳ جاري قراءة القطعة وتحليل تفاصيلها...")

        # 1. جلب بيانات القطعة
        product = get_shein_product(original_url)

        if not product or not product.get("full_title"):
            bot.edit_message_text("❌ تعذر قراءة عنوان هذه القطعة من رابط onelink تلقائياً. يُفضل نسخ رابط القطعة المباشر من المتصفح.", msg.chat.id, wait.message_id)
            continue

        # 2. صياغة النص المخصص بالذكاء الاصطناعي
        ai_caption = generate_caption_with_ai(product["full_title"])
        
        # 3. إعداد المنشور وإرساله
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
