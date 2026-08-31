import telebot
import re
import time
import os
import requests
import json
from flask import Flask, request
from playwright.sync_api import sync_playwright

# ─── التوكن ومفاتيح التشغيل ───
TOKEN = os.environ.get("BOT_TOKEN", "8888709197:AAEVCTpVticEzi-NBaWRdIQDmKJSxdRzA54")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyAD68JzBWieLXb9kE-7qOg-8p10_EkY518")

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
2. يجب أن يكون الكلام مطبقًا 100% على طبيعة المنتج (مثلاً: إذا كان مج أو كوب لا تتحدث عن اللبس بل عن القهوة والروقان، إذا كان مكياج تحدث عن النضارة، إذا كان فستان تحدث عن الكشخة والقصة).
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


def get_shein_product_with_browser(raw_url):
    """
    فتح الرابط بمتصفح متخفي لتجاوز حظر البوتات واستخراج البيانات
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-blink-features=AutomationControlled'
                ]
            )
            
            # إعدادات محاكاة متصفح آيفون حقيقي بدون بصمة بوت
            context = browser.new_context(
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
                viewport={'width': 393, 'height': 852},
                locale="ar-SA",
                device_scale_factor=3,
                is_mobile=True,
                has_touch=True
            )
            
            page = context.new_page()
            
            # اخفاء متغيرات التشفير والتحكم الآلي
            page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            """)
            
            # فتح الرابط مع إعطاء وقت أطول للتوجيهات (OneLink)
            page.goto(raw_url, wait_until="networkidle", timeout=45000)
            page.wait_for_timeout(4000)

            # استخراج عنوان ورابط الصورة
            title = page.evaluate("""() => {
                const metaOg = document.querySelector('meta[property="og:title"]') || document.querySelector('meta[name="twitter:title"]');
                if (metaOg && metaOg.content) return metaOg.content;
                return document.title;
            }""")

            image = page.evaluate("""() => {
                const metaImg = document.querySelector('meta[property="og:image"]') || document.querySelector('meta[name="twitter:image"]');
                if (metaImg && metaImg.content) return metaImg.content;
                return null;
            }""")

            browser.close()

            if title:
                title = re.sub(r"\s*\|\s*SHEIN.*$", "", title, flags=re.IGNORECASE).strip()

            if image and image.startswith("//"):
                image = "https:" + image

            if title and len(title) > 3 and "SHEIN" not in title and "OneLink" not in title:
                return {"full_title": title, "image": image}
            elif title and len(title) > 5:
                return {"full_title": title, "image": image}

    except Exception as e:
        print(f"Playwright Stealth Scraping Error: {e}")

    return None


@bot.message_handler(func=lambda m: True)
def handler(msg):
    text = msg.text.strip()
    urls = re.findall(r"https?://\S+", text)

    if not urls:
        bot.reply_to(msg, "❌ يرجى إرسال رابط المنتج")
        return

    for original_url in urls:
        wait = bot.reply_to(msg, "⏳ جاري فتح الرابط بمتصفح متخفي وقراءة تفاصيل القطعة...")

        product = get_shein_product_with_browser(original_url)

        if not product or not product.get("full_title"):
            bot.edit_message_text("❌ تعذر قراءة عنوان المنتج، يرجى التأكد من صحة الرابط أو المحاولة لاحقاً.", msg.chat.id, wait.message_id)
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
