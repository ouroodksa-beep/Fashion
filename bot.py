import os
import json
import urllib.parse
import asyncio
import threading
from openai import OpenAI
from flask import Flask, request, Response
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

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
# AI: تحليل نية المستخدم
# -------------------------
def analyze_intent(user_text):
    prompt = f"""You are a fashion/outfit coordinator AI for Shein e-commerce.

User wrote in Arabic: "{user_text}"

Analyze what they want and return ONLY this JSON:
{{
  "category": "short category name in Arabic",
  "pieces": [
    {{"name": "piece name in Arabic", "search": "English search query for Shein", "emoji": "👗"}},
    {{"name": "piece name in Arabic", "search": "English search query for Shein", "emoji": "👠"}},
    {{"name": "piece name in Arabic", "search": "English search query for Shein", "emoji": "👜"}}
  ]
}}

Rules:
- "فستان" or "dress" → dress + shoes + bag (3 pieces)
- "أطفال" or "kids" → outfit set + shoes + accessory (3 pieces)
- "ديكور" or "decor" → 3-4 matching decor items
- "مطبخ" or "kitchen" → 3-4 matching kitchen items
- "رجالي" or "men" → shirt + pants + shoes + watch (4 pieces)
- "رياضي" or "sport" → sport outfit + shoes + bag (3 pieces)
- "شنط" or "bags" → handbag + wallet + belt (3 pieces)
- "حذاء" or "shoes" → shoes + socks + shoe care (3 pieces)
- Always 3-4 pieces that MATCH in style/color
"""

    try:
        res = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        content = res.choices[0].message.content.strip()
        content = content.replace("```json", "").replace("```", "").strip()
        return json.loads(content)
    except Exception as e:
        print(f"Intent error: {e}")
        return {
            "category": user_text,
            "pieces": [
                {"name": "فستان", "search": "women dress", "emoji": "👗"},
                {"name": "حذاء", "search": "women shoes", "emoji": "👠"},
                {"name": "شنطة", "search": "women bag", "emoji": "👜"}
            ]
        }


# -------------------------
# بناء رابط Shein
# -------------------------
def build_shein_link(query):
    encoded = urllib.parse.quote(query)
    return f"https://www.shein.com/search?keyword={encoded}"


# -------------------------
# بناء التنسيق
# -------------------------
def build_outfit(intent_data):
    pieces = intent_data["pieces"]
    outfit = []

    for piece in pieces:
        link = build_shein_link(piece["search"])
        outfit.append({
            "name": piece["name"],
            "emoji": piece["emoji"],
            "search": piece["search"],
            "shein_link": link
        })

    return outfit


# -------------------------
# صياغة الرد
# -------------------------
def format_outfit(outfit, category):
    text = f"✨ تنسيق كامل من Shein - {category}\n\n"

    for item in outfit:
        text += f"{item['emoji']} {item['name']}\n"
        text += f"🔍 بحث Shein: {item['search']}\n"
        text += f"🔗 [افتح Shein]({item['shein_link']})\n"
        text += "\n" + "─" * 25 + "\n\n"

    text += "💡 *نصائح للتنسيق:*\n"
    text += "• اختار نفس درجة اللون في كل القطع\n"
    text += "• الفستان الطويل يبقى مع كعب عالي\n"
    text += "• الشنطة تكون بنفس لون الحذاء\n\n"
    text += "🛍️ اضغط على أي رابط واشتري مباشرة من Shein!"

    return text


# -------------------------
# HANDLERS
# -------------------------
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text("🧠 بجهزلك تنسيق كامل من Shein...")

    intent = analyze_intent(text)
    print(f"📝 User: {text} → {intent['category']}")

    outfit = build_outfit(intent)
    result = format_outfit(outfit, intent["category"])

    if len(result) > 4000:
        result = result[:4000] + "\n\n..."

    await update.message.reply_text(result, parse_mode="Markdown", disable_web_page_preview=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👗 *Smart Stylist - Shein Edition* ✨\n\n"
        "اكتب أي حاجة وأنا هجهزلك تنسيق كامل من Shein:\n\n"
        "👗 *فستان سهرة* → فستان + كعب + شنطة\n"
        "👶 *طقم أطفال* → طقم + حذاء + إكسسوار\n"
        "🛋️ *ديكور صالة* → سجادة + إضاءة + وسائد\n"
        "👔 *رجالي* → قميص + بنطلون + حذاء\n"
        "🏃 *رياضي* → طقم رياضي + حذاء + شنطة\n"
        "🍳 *مطبخ* → منظمات + أدوات + تخزين\n\n"
        "🛒 *كل الروابط بتوديك مباشرة على Shein!*",
        parse_mode="Markdown"
    )


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

        # ✅ الحل: نستخدم bot.send_message مباشرة بدل application.process_update
        update = Update.de_json(update_data, application.bot)

        # نتأكد إن فيه message
        if update.message and update.message.text:
            text = update.message.text
            chat_id = update.message.chat_id

            print(f"💬 Message from {chat_id}: {text}")

            # لو /start
            if text == "/start":
                asyncio.run(send_start_message(chat_id))
            else:
                # معالجة الرسالة
                asyncio.run(process_message(chat_id, text))

        return Response('OK', status=200)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return Response('Error', status=500)


async def send_start_message(chat_id):
    """بيبعت رسالة البداية"""
    await application.bot.send_message(
        chat_id=chat_id,
        text="👗 *Smart Stylist - Shein Edition* ✨\n\n"
             "اكتب أي حاجة وأنا هجهزلك تنسيق كامل من Shein:\n\n"
             "👗 *فستان سهرة* → فستان + كعب + شنطة\n"
             "👶 *طقم أطفال* → طقم + حذاء + إكسسوار\n"
             "🛋️ *ديكور صالة* → سجادة + إضاءة + وسائد\n"
             "👔 *رجالي* → قميص + بنطلون + حذاء\n"
             "🏃 *رياضي* → طقم رياضي + حذاء + شنطة\n"
             "🍳 *مطبخ* → منظمات + أدوات + تخزين\n\n"
             "🛒 *كل الروابط بتوديك مباشرة على Shein!*",
        parse_mode="Markdown"
    )


async def process_message(chat_id, text):
    """بيبعت تنسيق كامل"""
    await application.bot.send_message(
        chat_id=chat_id,
        text="🧠 بجهزلك تنسيق كامل من Shein..."
    )

    intent = analyze_intent(text)
    print(f"📝 User: {text} → {intent['category']}")

    outfit = build_outfit(intent)
    result = format_outfit(outfit, intent["category"])

    if len(result) > 4000:
        result = result[:4000] + "\n\n..."

    await application.bot.send_message(
        chat_id=chat_id,
        text=result,
        parse_mode="Markdown",
        disable_web_page_preview=True
    )


# -------------------------
# MAIN
# -------------------------
def main():
    print("Smart Stylist - Shein Edition starting...")

    # Initialize
    asyncio.run(init_app())

    # Webhook URL
    webhook_path = f"/{BOT_TOKEN}"
    webhook_url = f"https://{WEBHOOK_HOST}{webhook_path}"

    print(f"Setting webhook: {webhook_url}")

    # سجل الـ webhook
    asyncio.run(set_webhook(webhook_url))

    # تشغيل Flask server
    print(f"✅ Server running on port {PORT}")
    app.run(host='0.0.0.0', port=PORT)


async def init_app():
    """Initialize التطبيق"""
    await application.initialize()


async def set_webhook(url):
    """سجل الـ webhook"""
    await application.bot.set_webhook(url=url)


if __name__ == "__main__":
    main()
  "pieces": [
    {{"name": "piece name in Arabic", "search": "English search query for Shein", "emoji": "👗"}},
    {{"name": "piece name in Arabic", "search": "English search query for Shein", "emoji": "👠"}},
    {{"name": "piece name in Arabic", "search": "English search query for Shein", "emoji": "👜"}}
  ]
}}

Rules:
- "فستان" or "dress" → dress + shoes + bag (3 pieces)
- "أطفال" or "kids" → outfit set + shoes + accessory (3 pieces)
- "ديكور" or "decor" → 3-4 matching decor items
- "مطبخ" or "kitchen" → 3-4 matching kitchen items
- "رجالي" or "men" → shirt + pants + shoes + watch (4 pieces)
- "رياضي" or "sport" → sport outfit + shoes + bag (3 pieces)
- "شنط" or "bags" → handbag + wallet + belt (3 pieces)
- "حذاء" or "shoes" → shoes + socks + shoe care (3 pieces)
- Always 3-4 pieces that MATCH in style/color
"""

    try:
        res = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        content = res.choices[0].message.content.strip()
        content = content.replace("```json", "").replace("```", "").strip()
        return json.loads(content)
    except Exception as e:
        print(f"Intent error: {e}")
        return {
            "category": user_text,
            "pieces": [
                {"name": "فستان", "search": "women dress", "emoji": "👗"},
                {"name": "حذاء", "search": "women shoes", "emoji": "👠"},
                {"name": "شنطة", "search": "women bag", "emoji": "👜"}
            ]
        }


# -------------------------
# بناء رابط Shein
# -------------------------
def build_shein_link(query):
    encoded = urllib.parse.quote(query)
    return f"https://www.shein.com/search?keyword={encoded}"


# -------------------------
# بناء التنسيق
# -------------------------
def build_outfit(intent_data):
    pieces = intent_data["pieces"]
    outfit = []

    for piece in pieces:
        link = build_shein_link(piece["search"])
        outfit.append({
            "name": piece["name"],
            "emoji": piece["emoji"],
            "search": piece["search"],
            "shein_link": link
        })

    return outfit


# -------------------------
# صياغة الرد
# -------------------------
def format_outfit(outfit, category):
    text = f"✨ تنسيق كامل من Shein - {category}\n\n"

    for item in outfit:
        text += f"{item['emoji']} {item['name']}\n"
        text += f"🔍 بحث Shein: {item['search']}\n"
        text += f"🔗 [افتح Shein]({item['shein_link']})\n"
        text += "\n" + "─" * 25 + "\n\n"

    text += "💡 *نصائح للتنسيق:*\n"
    text += "• اختار نفس درجة اللون في كل القطع\n"
    text += "• الفستان الطويل يبقى مع كعب عالي\n"
    text += "• الشنطة تكون بنفس لون الحذاء\n\n"
    text += "🛍️ اضغط على أي رابط واشتري مباشرة من Shein!"

    return text


# -------------------------
# HANDLERS
# -------------------------
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text("🧠 بجهزلك تنسيق كامل من Shein...")

    intent = analyze_intent(text)
    print(f"📝 User: {text} → {intent['category']}")

    outfit = build_outfit(intent)
    result = format_outfit(outfit, intent["category"])

    if len(result) > 4000:
        result = result[:4000] + "\n\n..."

    await update.message.reply_text(result, parse_mode="Markdown", disable_web_page_preview=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👗 *Smart Stylist - Shein Edition* ✨\n\n"
        "اكتب أي حاجة وأنا هجهزلك تنسيق كامل من Shein:\n\n"
        "👗 *فستان سهرة* → فستان + كعب + شنطة\n"
        "👶 *طقم أطفال* → طقم + حذاء + إكسسوار\n"
        "🛋️ *ديكور صالة* → سجادة + إضاءة + وسائد\n"
        "👔 *رجالي* → قميص + بنطلون + حذاء\n"
        "🏃 *رياضي* → طقم رياضي + حذاء + شنطة\n"
        "🍳 *مطبخ* → منظمات + أدوات + تخزين\n\n"
        "🛒 *كل الروابط بتوديك مباشرة على Shein!*",
        parse_mode="Markdown"
    )


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

        # ✅ الحل: نستخدم application.update_queue.put() بدل process_update()
        update = Update.de_json(update_data, application.bot)
        application.update_queue.put_nowait(update)

        return Response('OK', status=200)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return Response('Error', status=500)


# -------------------------
# MAIN
# -------------------------
def main():
    print("Smart Stylist - Shein Edition starting...")

    # إضافة الـ handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

    # ✅ الحل: نستخدم asyncio.run() عشان نinitialize الـ application
    async def init_app():
        await application.initialize()
        await application.start()

    asyncio.run(init_app())

    # Webhook URL
    webhook_path = f"/{BOT_TOKEN}"
    webhook_url = f"https://{WEBHOOK_HOST}{webhook_path}"

    print(f"Setting webhook: {webhook_url}")

    # سجل الـ webhook
    application.bot.set_webhook(url=webhook_url)

    # تشغيل Flask server
    print(f"✅ Server running on port {PORT}")
    app.run(host='0.0.0.0', port=PORT)


if __name__ == "__main__":
    main()
