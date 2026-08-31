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


def resolve_shein_link(url):
    """
    استخراج الرابط الحقيقي للمنتج وتجنب روابط التطبيقات Deep Links
    """
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ar,en-US;q=0.9,en;q=0.8"
    })
    
    try:
        res = session.get(url, allow_redirects=True, timeout=12)
        final_url = res.url
        
        # إذا تحول الرابط لرابط ويب عادي يحتوي على p- أو -p-
        if "shein.com" in final_url and ("-p-" in final_url or "p-" in final_url):
            return final_url
            
        # محاولة استخراج الرابط المباشر من الـ HTML إذا كان هناك Meta Refresh
        soup = BeautifulSoup(res.text, "html.parser")
        meta_refresh = soup.find("meta", attrs={"http-equiv": re.compile(r"refresh", re.I)})
        if meta_refresh and "url=" in meta_refresh.get("content", "").lower():
            extracted_url = meta_refresh["content"].lower().split("url=")[-1].strip()
            if extracted_url.startswith("http"):
                return extracted_url

        return final_url
    except Exception as e:
        print(f"Resolve Link Error: {e}")
        return url


def get_shein_product(raw_url):
    """
    تفكيك الرابط المختصر أولاً ثم كشط بيانات المنتج المباشرة
    """
    # 1. فك التوجيه للحصول على رابط الويب الصريح
    target_url = resolve_shein_link(raw_url)
    print(f"Resolved Target URL: {target_url}")

    # 2. إرسال الرابط النهائي إلى ScraperAPI
    api_url = f"http://api.scraperapi.com?api_key={SCRAPERAPI_KEY}&url={requests.utils.quote(target_url)}"

    try:
        r = requests.get(api_url, timeout=30)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")

            title = None
            image = None

            # استخراج اسم المنتج والصورة من الوسوم المباشرة
            og_title = soup.select_one('meta[property="og:title"]') or soup.select_one('meta[name="twitter:title"]')
            if og_title and og_title.get("content"):
                title = og_title["content"].strip()

            og_image = soup.select_one('meta[property="og:image"]') or soup.select_one('meta[name="twitter:image"]')
            if og_image and og_image.get("content"):
                image = og_image["content"].strip()

            # البديل 1: البحث في بيانات JSON-LD الداخلية
            if not title:
                for script in soup.find_all('script', type='application/ld+json'):
                    try:
                        data = json.loads(script.string)
                        if isinstance(data, dict) and 'name' in data:
                            title = data.get('name')
                            if 'image' in data:
                                img_val = data['image']
                                image = img_val[0] if isinstance(img_val, list) else img_val
                            break
                    except Exception:
                        continue

            # البديل 2: الوسم العادي <title>
            if not title and soup.title:
                title = soup.title.get_text(strip=True)
                title = re.sub(r"\s*\|\s*SHEIN.*$", "", title, flags=re.IGNORECASE)

            # تنظيف وتنسيق رابط الصورة
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
        wait = bot.reply_to(msg, "⏳ جاري فك الرابط وتحليل المنتج بالذكاء الاصطناعي...")

        product = get_shein_product(original_url)

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
