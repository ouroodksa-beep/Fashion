import os
import asyncio
import json
import urllib.parse
from openai import OpenAI
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ⚠️ HARDCODED KEYS
BOT_TOKEN = "8888709197:AAHID3wJwsQiJqcQ7cemP31CKNSzkrP79wM"
OPENAI_API_KEY = "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"

client = OpenAI(api_key=OPENAI_API_KEY)


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
# MAIN - POLLING مع منع Conflict
# -------------------------
async def main():
    print("Smart Stylist - Shein Edition starting...")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

    await app.initialize()
    await app.start()

    # ✅ الحل: نمسح الـ pending updates ونمنع الـ conflict
    print("Starting polling with drop_pending_updates=True...")
    await app.updater.start_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True  # ← ده بيمسح الـ updates القديمة
    )

    print("✅ Bot is running!")
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
