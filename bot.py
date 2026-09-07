import telebot
import re
import time
import requests
import json
from bs4 import BeautifulSoup
from flask import Flask, request

# ─── المفاتيح المباشرة والتأكيد ───
TOKEN = "8888709197:AAEVCTpVticEzi-NBaWRdIQDmKJSxdRzA54"
GEMINI_API_KEY = "AIzaSyAD68JzBWieLXb9kE-7qOg-8p10_EkY518"

bot = telebot.TeleBot(TOKEN)


def generate_caption_with_ai(product_title):
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

    # تصحيح اسم الموديل إلى الإصدار المستقر المعتمد gemini-1.5-flash
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    try:
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=15)
        if response.status_code == 200:
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text'].strip()
        else:
            print(f"Gemini API Error Status: {response.status_code}, Response: {response.text}")
    except Exception as e:
        print(f"Gemini Exception: {e}")

    return None


def get_shein_product(raw_url):
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "ar-SA,ar;q=0.9,en-US;q=0.8,en;q=0.7"
    }

    try:
        res = session.get(raw_url, headers=headers, allow_redirects=True, timeout=12)
        final_url = res.url
        
        title = None
        image = None

        soup = BeautifulSoup(res.text, "html.parser")
        
        for selector in ['meta[property="og:title"]', 'meta[name="twitter:title"]', 'title']:
            tag = soup.select_one(selector)
            if tag:
                content = tag.get("content") or tag.text
                if content and len(content.strip()) > 5:
                    title = content.strip()
                    break

        for img_selector in ['meta[property="og:image"]', 'meta[name="twitter:image"]']:
            img_tag = soup.select_one(img_selector)
            if img_tag and img_tag.get("content"):
                image = img_tag["content"].strip()
                break

        if not title or ("SHEIN" in title and len(title) < 15):
            goods_id_match = re.search(r"p-(\d+)|goods-(\d+)|id=(\d+)", final_url)
            if goods_id_match:
                goods_id = next(g for g in goods_id_match.groups() if g)
                api_url = f"https://ar.shein.com/api/product/detail?goods_id={goods_id}"
                api_res = session.get(api_url, headers=headers, timeout=10)
                if api_res.status_code == 200:
                    data = api_res.json()
                    if "info" in data and "goods_name" in data["info"]:
                        title = data["info"]["goods_name"]
                        image = data["info"].get("goods_img")

        if title:
            title = re.sub(r"\s*\|\s*SHEIN.*$", "", title, flags=re.IGNORECASE).strip()
            title = re.sub(r"^SHEIN\s*", "", title, flags=re.IGNORECASE).strip()

        if image and image.startswith("//"):
            image = "https:" + image

        if title and len(title) > 3:
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
        wait = bot.reply_to(msg, "⏳ جاري قراءة تفاصيل القطعة وصياغة الوصف الخاص بها...")

        product = get_shein_product(original_url)

        if not product or not product.get("full_title"):
            bot.edit_message_text(
                "❌ **تعذر قراءة عنوان هذه القطعة تلقائياً.**\n\n"
                "سيرفر شي إن يفرض حظراً على قراءة هذا الرابط حالياً.",
                msg.chat.id, 
                wait.message_id,
                parse_mode="Markdown"
            )
            continue

        ai_caption = generate_caption_with_ai(product["full_title"])

        if not ai_caption:
            bot.edit_message_text(
                "❌ **حدث خطأ في استجابة الذكاء الاصطناعي.**", 
                msg.chat.id, 
                wait.message_id,
                parse_mode="Markdown"
            )
            continue

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

PORT = 10000
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
