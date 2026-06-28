import os
import json
import urllib.parse
import asyncio
import threading
from openai import OpenAI
from flask import Flask, request, Response
from telegram import Update, InputMediaPhoto
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
from bs4 import BeautifulSoup

# ⚠️ HARDCODED KEYS
BOT_TOKEN = "8888709197:AAHID3wJwsQiJqcQ7cemP31CKNSzkrP79wM"
OPENAI_API_KEY = "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"

PORT = 10000
WEBHOOK_HOST = "fashion-y26k.onrender.com"

client = OpenAI(api_key=OPENAI_API_KEY)

app = Flask(__name__)

# Telegram Application
application = Application.builder().token(BOT_TOKEN).build()


# -------------------------
# AI: كتابة بوست جذاب
# -------------------------
def generate_caption(product_title, product_description=""):
    prompt = f"""You are a professional fashion/marketing copywriter for social media.

Product: {product_title}
Description: {product_description}

Write an attractive Arabic social media post about this product. Make it catchy, engaging, and persuasive. Use emojis. Include a call to action.

Return ONLY the post text, nothing else.
"""

    try:
        res = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return res.choices[0].message.content.strip()
    except Exception as e:
        print(f"Caption error: {e}")
        return f"✨ {product_title}\n\nمتوفر الآن على Shein!\n\n#fashion #style #shein"


# -------------------------
# استخراج بيانات المنتج من Shein
# -------------------------
def extract_shein_data(url):
    """يستخرج صورة وعنوان المنتج من رابط Shein"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')

        # استخراج العنوان
        title = ""
        title_tag = soup.find('h1', class_='product-intro__head-name') or \
                   soup.find('h1', {'data-selenium': 'product-title'}) or \
                   soup.find('title')
        if title_tag:
            title = title_tag.get_text().strip()

        # استخراج الصورة
        image_url = ""
        img_tag = soup.find('img', class_='product-intro__main-image') or \
                 soup.find('img', {'data-selenium': 'product-image'}) or \
                 soup.find('meta', property='og:image')
        
        if img_tag:
            if img_tag.name == 'meta':
                image_url = img_tag.get('content', '')
            else:
                image_url = img_tag.get('src', '') or img_tag.get('data-src', '')

        # لو مفيش صورة، نستخدم صورة افتراضية
        if not image_url:
            image_url = "https://img.ltwebstatic.com/images3_pi/2021/04/09/1617973305e8b6c0db1f9e8c1e5c1e5c1e5c1e5c1e.webp"

        return {
            "title": title or "منتج Shein",
            "image": image_url,
            "url": url
        }
    except Exception as e:
        print(f"Extract error: {e}")
        return {
            "title": "منتج Shein",
            "image": "https://img.ltwebstatic.com/images3_pi/2021/04/09/1617973305e8b6c0db1f9e8c1e5c1e5c1e5c1e5c1e.webp",
            "url": url
        }


# -------------------------
# FLASK ROUTES
# -------------------------
@app.route('/')
def home():
    return "Smart Stylist Bot is running! ✅"


@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    """يستقبل الـ updates من Telegram"""
    try:
        update_data = request.get_json(force=True)
        print(f"📩 Received update: {json.dumps(update_data, ensure_ascii=False)[:200]}")

        update = Update.de_json(update_data, application.bot)

        if update.message and update.message.text:
            text = update.message.text
            chat_id = update.message.chat_id

            print(f"💬 Message from {chat_id}: {text}")

            # ✅ لو الرسالة فيها لينك Shein
            if "shein.com" in text or "shein" in text.lower():
                thread = threading.Thread(
                    target=process_shein_link_sync,
                    args=(chat_id, text)
                )
                thread.start()
            elif text == "/start":
                thread = threading.Thread(
                    target=process_start_sync,
                    args=(chat_id,)
                )
                thread.start()

        return Response('OK', status=200)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return Response('Error', status=500)


def process_start_sync(chat_id):
    """بيبعت رسالة البداية"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(send_start_message(chat_id))
    finally:
        loop.close()


def process_shein_link_sync(chat_id, text):
    """بيتعامل مع لينك Shein"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(process_shein_link(chat_id, text))
    finally:
        loop.close()


async def send_start_message(chat_id):
    """بيبعت رسالة البداية"""
    await application.bot.send_message(
        chat_id=chat_id,
        text="👗 *Smart Stylist - Shein Edition* ✨\n\n"
             "ابعتلي لينك أي قطعة من Shein وأنا هجهزلك:\n"
             "📸 صورة المنتج\n"
             "✍️ بوست جذاب\n"
             "🔗 رابط المنتج\n\n"
             "جرب دلوقتي!",
        parse_mode="Markdown"
    )


async def process_shein_link(chat_id, text):
    """بيبعت صورة + بوست + رابط"""
    # استخراج الرابط من الرسالة
    import re
    urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
    
    if not urls:
        await application.bot.send_message(
            chat_id=chat_id,
            text="❌ مفيش لينك صحيح. ابعت لينك من Shein."
        )
        return

    url = urls[0]
    print(f"🔗 Processing URL: {url}")

    # استخراج بيانات المنتج
    await application.bot.send_message(
        chat_id=chat_id,
        text="⏳ بجيب بيانات المنتج..."
    )

    product_data = extract_shein_data(url)

    # كتابة البوست
    caption = generate_caption(product_data["title"])

    # تجميع الرسالة النهائية
    final_text = f"{caption}\n\n🔗 [اشتري دلوقتي]({url})"

    print(f"📸 Image: {product_data['image']}")
    print(f"✍️ Caption: {caption[:100]}...")

    # إرسال الصورة مع النص
    try:
        await application.bot.send_photo(
            chat_id=chat_id,
            photo=product_data["image"],
            caption=final_text,
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Photo send error: {e}")
        # لو الصورة مبعتتش، نبعت النص بس
        await application.bot.send_message(
            chat_id=chat_id,
            text=final_text,
            parse_mode="Markdown",
            disable_web_page_preview=False
        )


# -------------------------
# MAIN
# -------------------------
def main():
    print("Smart Stylist - Shein Edition starting...")

    # Initialize
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(application.initialize())
    loop.close()

    # Webhook URL
    webhook_path = f"/{BOT_TOKEN}"
    webhook_url = f"https://{WEBHOOK_HOST}{webhook_path}"

    print(f"Setting webhook: {webhook_url}")

    # سجل الـ webhook
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(application.bot.set_webhook(url=webhook_url))
    loop.close()

    print(f"✅ Server running on port {PORT}")
    app.run(host='0.0.0.0', port=PORT)


if __name__ == "__main__":
    main()
