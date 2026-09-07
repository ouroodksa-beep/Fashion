import os
import re
import time
import json
import requests
from bs4 import BeautifulSoup
from flask import Flask, request
import telebot

# ─── الإعدادات والمفاتيح ───
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8888709197:AAEVCTpVticEzi-NBaWRdIQDmKJSxdRzA54")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyAD68JzBWieLXb9kE-7qOg-8p10_EkY518")
PROXY_URL = os.environ.get("PROXY_URL")

bot = telebot.TeleBot(BOT_TOKEN)

# ─── صياغة الوصف بالذكاء الاصطناعي عبر API مباشر (بدون مكتبات إضافية) ───
def generate_creative_description(title):
    if not GEMINI_KEY:
        return f"✨ {title}"

    prompt = f"""
    أنت خبير تسويق إلكتروني محترف لقناة "صيدات وعروض" شهيرة في السعودية.
    قم بتحليل عنوان المنتج التالي من موقع شي إن (SHEIN):
    Title: "{title}"

    المطلوب كتابة بوست تسويقي جذاب جداً ومحمس بالشروط التالية:
    1. اكتب باللهجة السعودية / الخليجية الممتعة والسلسة.
    2. لا ترص الكلام رص ولا تذكر المواصفات كقائمة جافة.
    3. ابدأ بعبارة خاطفة ومحمسة تعبر عن شياكة المنتج وفخامته (مثل: كشخة، تجنن، قطعة المأنتكة، خيال، كملي إطلالتك..).
    4. حدد نوع المنتج ولونه الأساسي بدقة وبدون أي تلخبط.
    5. ركز على إبراز جمال المنتج ودعوة المتابع للشراء قبل نفاذ الكمية أو انتهاء العرض.
    6. استخدم إيموجيز جذابة وفخمة تناسب نوع القطعة (مثل: 👜, ✨, 👗, 👠, 🤍, 🔥).
    7. اجعل البوست في حدود 2 إلى 4 سطور فقط ليكون خفيفاً وسهل القراءة.
    8. أعطني النص النهائي الجاهز للنشر مباشرة بدون أي مقدمات أو شروحات.
    """

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            desc = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            return desc
        else:
            print(f"Gemini API Error Status: {response.status_code}")
            return "✨ قطعة كشخة وتصميم خيال لا تفوتكم!"
    except Exception as e:
        print(f"Gemini API Exception: {e}")
        return "✨ قطعة كشخة وتصميم خيال لا تفوتكم!"

# ─── فحص روابط شي إن ───
def is_shein_url(url):
    return any(domain in url.lower() for domain in ["shein.com", "shein.top", "onelink.shein.com"])

# ─── جلب بيانات المنتج من شي إن ───
def get_shein_product(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://www.google.com/",
    }

    proxies = {"http": PROXY_URL, "https": PROXY_URL} if PROXY_URL else None

    try:
        session = requests.Session()
        session.headers.update(headers)
        
        res = session.get(url, timeout=12, proxies=proxies, allow_redirects=True)
        final_url = res.url

        goods_id_match = re.search(r'-p-(\d+)\.html', final_url) or re.search(r'goods_id=(\d+)', final_url) or re.search(r'g-([a-zA-Z0-9]+)', final_url)
        
        if goods_id_match:
            goods_id = goods_id_match.group(1)
            api_url = f"https://m.shein.com/us/product-goodsdetail-json-{goods_id}.html"
            api_res = session.get(api_url, timeout=10, proxies=proxies)

            if api_res.status_code == 200:
                data = api_res.json()
                detail = data.get("goodsDetail", {})
                if detail:
                    title = detail.get("goods_name") or detail.get("goods_url_name")
                    image = detail.get("goods_img") or detail.get("goods_thumb")
                    if image and not image.startswith("http"):
                        image = "https:" + image
                    if title:
                        return {"full_title": title, "image": image}

        soup = BeautifulSoup(res.text, "html.parser")

        title = None
        og_title = soup.select_one('meta[property="og:title"]')
        if og_title:
            title = og_title.get("content", "").strip()
        if not title:
            title_tag = soup.select_one("title")
            if title_tag:
                title = title_tag.get_text(strip=True)
                title = re.sub(r"\s*\|\s*SHEIN.*$", "", title, flags=re.IGNORECASE)

        image = None
        og_image = soup.select_one('meta[property="og:image"]')
        if og_image:
            image = og_image.get("content", "").strip()

        if image:
            if image.startswith("//"):
                image = "https:" + image
            elif image.startswith("/"):
                image = "https://www.shein.com" + image

        if title:
            return {"full_title": title, "image": image}

    except Exception as e:
        print(f"Error fetching product: {e}")

    return None

# ─── معالج رسائل التليجرام ───
@bot.message_handler(func=lambda m: True)
def handler(msg):
    text = msg.text.strip()
    urls = re.findall(r"https?://\S+", text)

    if not urls:
        bot.reply_to(msg, "❌ يرجى إرسال رابط المنتج من شي إن")
        return

    for original_url in urls:
        if not is_shein_url(original_url):
            bot.reply_to(msg, "❌ الرابط يجب أن يكون من شي إن (shein.com)")
            continue

        wait = bot.reply_to(msg, "⏳ جاري قراءة المنتج وصياغة العرض...")

        product = get_shein_product(original_url)

        if not product:
            bot.edit_message_text("❌ تعذر قراءة بيانات المنتج، حاول مرة ثانية", msg.chat.id, wait.message_id)
            continue

        marketing_desc = generate_creative_description(product["full_title"])
        post = f"{marketing_desc}\n\n🛒 **رابط الطلب المباشر:**\n{original_url}"

        try:
            if product["image"]:
                bot.send_photo(msg.chat.id, product["image"], caption=post, parse_mode="Markdown")
            else:
                bot.send_message(msg.chat.id, post, parse_mode="Markdown")
            bot.delete_message(msg.chat.id, wait.message_id)
        except Exception as e:
            print(f"Error sending: {e}")
            try:
                bot.send_message(msg.chat.id, post)
                bot.delete_message(msg.chat.id, wait.message_id)
            except Exception as e2:
                bot.edit_message_text("❌ حدث خطأ في الإرسال", msg.chat.id, wait.message_id)

# ─── إعدادات السيرفر والـ Webhook ───
app = Flask(__name__)

WEBHOOK_HOST = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
WEBHOOK_PORT = int(os.environ.get("PORT", 10000))
WEBHOOK_URL_BASE = f"https://{WEBHOOK_HOST}" if WEBHOOK_HOST else None
WEBHOOK_URL_PATH = f"/webhook/{BOT_TOKEN}"

@app.route("/")
def index():
    return "🤖 البوت يعمل بنجاح مع الذكاء الاصطناعي"

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
