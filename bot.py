import os
import asyncio
from openai import OpenAI
from playwright.async_api import async_playwright
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("8888709197:AAHID3wJwsQiJqcQ7cemP31CKNSzkrP79wM")
OPENAI_API_KEY = os.getenv("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")

client = OpenAI(api_key=OPENAI_API_KEY)


# -------------------------
# SEARCH CATEGORY MAP
# -------------------------
CATEGORIES = {
    "فساتين": "women dress elegant outfit",
    "اطفال": "kids outfit set cute fashion",
    "مطبخ": "kitchen decor organizer aesthetic",
    "ديكور": "living room decor modern aesthetic"
}


# -------------------------
# CLASSIFY USER INTENT
# -------------------------
def classify(text):
    if "فساتين" in text:
        return "فساتين"
    elif "اطفال" in text:
        return "اطفال"
    elif "مطبخ" in text:
        return "مطبخ"
    elif "ديكور" in text:
        return "ديكور"
    return "فساتين"


# -------------------------
# SEARCH SHEIN
# -------------------------
async def search_shein(query):
    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.goto(f"https://www.shein.com/search?keyword={query}")
        await page.wait_for_timeout(5000)

        items = await page.query_selector_all(".S-product-item__wrapper")

        for item in items[:25]:
            try:
                title = await item.inner_text()
                link = await item.query_selector("a")
                href = await link.get_attribute("href")

                if href:
                    results.append({
                        "title": title.strip()[:120],
                        "url": "https://www.shein.com" + href
                    })
            except:
                continue

        await browser.close()

    return results


# -------------------------
# AI PRODUCT ANALYSIS (IMPORTANT PART)
# -------------------------
def analyze_product(product):
    prompt = f"""
You are a fashion classifier.

Product: {product['title']}

Return ONLY JSON:
{
  "type": "dress|shoes|bag|other",
  "style": "casual|elegant|party|kids|home",
  "color": "guess color",
  "formality": 1-10
}
"""

    try:
        res = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        return eval(res.choices[0].message.content)
    except:
        return {
            "type": "other",
            "style": "casual",
            "color": "unknown",
            "formality": 5
        }


# -------------------------
# BUILD SMART OUTFITS
# -------------------------
def build_smart_outfits(products):
    analyzed = []

    for p in products:
        meta = analyze_product(p)
        p.update(meta)
        analyzed.append(p)

    dresses = [p for p in analyzed if p["type"] == "dress"]
    shoes = [p for p in analyzed if p["type"] == "shoes"]
    bags = [p for p in analyzed if p["type"] == "bag"]

    outfits = []

    for i in range(min(5, len(dresses), len(shoes), len(bags))):
        outfits.append([
            dresses[i],
            shoes[i],
            bags[i]
        ])

    return outfits


# -------------------------
# FORMAT OUTPUT
# -------------------------
def format_outfits(outfits, category):
    text = f"✨ تنسيقات ذكية - {category}\n\n"

    for i, outfit in enumerate(outfits, 1):
        text += f"👗 تنسيق {i}\n\n"

        for item in outfit:
            text += f"• {item['type']} - {item['title']}\n{item['url']}\n\n"

        text += "----------------------\n\n"

    return text


# -------------------------
# HANDLER
# -------------------------
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    await update.message.reply_text("🧠 بفهم الستايل وبعمل تنسيقات ذكية...")

    category = classify(text)
    query = CATEGORIES[category]

    products = await search_shein(query)

    if not products:
        await update.message.reply_text("❌ مفيش نتائج")
        return

    outfits = build_smart_outfits(products)

    result = format_outfits(outfits, category)

    await update.message.reply_text(result)


# -------------------------
# START
# -------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👗 ابعتي: فساتين / اطفال / مطبخ / ديكور")


# -------------------------
# RUN (NO WEBHOOK)
# -------------------------
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

    print("Smart Stylist running...")
    app.run_polling()


if __name__ == "__main__":
    main()
