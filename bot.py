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
    تتبع التحويلات لفك روابط onelink والوصول للرابط المباشر
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
        }
        res = requests.get(url, headers=headers, allow_redirects=True, timeout=12)
        return res.url
    except Exception as e:
        print(f"Redirect error: {e}")
        return url


def get_shein_product(raw_url):
    """
    جلب بيانات المنتج بعد فك الروجيه واستخراج الميتا داتا
    """
    final_url = resolve_final_url(raw_url)
    api_url = f"http://api.scraperapi.com?api_key={SCRAPERAPI_KEY}&url={requests.utils.quote(final_url)}&render=true&country_code=us"

    try:
        r = requests.get(api_url, timeout=40)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            title = None
            image = None

            # البحث عن العنوان في وسوم الميتا المختلفة
            for selector in ['meta[property="og:title"]', 'meta[name="twitter:title"]', 'title']:
                tag = soup.select_one(selector)
                if tag:
                    content = tag.get("content") or tag.text
                    if content and len(content.strip()) > 5:
                        title = content.strip()
                        break

            # البحث عن الصورة
            for img_selector in ['meta[property="og:image"]', 'meta[name="twitter:image"]']:
                img_tag = soup.select_one(img_selector)
                if img_tag and img_tag.get("content"):
                    image = img_tag["content"].strip()
                    break

            if title:
                # تنظيف اسم المنتج من العبارات الزائدة
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
        # معرفة ما إذا كانت الرسالة تحتوي على اسم للمنتج بجانب الرابط
        user_custom_title = text.replace(original_url, "").strip()

        wait = bot.reply_to(msg, "⏳ جاري تحليل القطعة وتجهيز المنشور...")

        product_title = None
        product_image = None

        # 1. إذا كتبتِ اسم القطعة بنفسك نعتمد عليه فوراً
        if user_custom_title and len(user_custom_title) > 2:
            product_title = user_custom_title
        else:
            # 2. وإلا يحاول البوت استخراجه تلقائياً
            product = get_shein_product(original_url)
            if product:
                product_title = product.get("full_title")
                product_image = product.get("image")

        if not product_title:
            bot.edit_message_text(
                "❌ تعذر قراءة عنوان القطعة من رابط onelink تلقائياً.\n\n"
                "💡 **حل سريع:** يرجى كتابة اسم القطعة مع الرابط في نفس الرسالة\n"
                "مثال: `فستان أسود أنيق https://onelink.shein.com/...`",
                msg.chat.id,
                wait.message_id,
                parse_mode="Markdown"
            )
            continue

        # 3. صياغة الإعلان بالذكاء الاصطناعي
        ai_caption = generate_caption_with_ai(product_title)
        post = f"{ai_caption}\n\n🔗 {original_url}"

        try:
            if product_image:
                bot.send_photo(msg.chat.id, product_image, caption=post)
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
