import telebot
import re
import time
import random
import os
import requests
import json
from bs4 import BeautifulSoup
from flask import Flask, request

TOKEN = os.environ.get("BOT_TOKEN", "8888709197:AAEVCTpVticEzi-NBaWRdIQDmKJSxdRzA54")
bot = telebot.TeleBot(TOKEN)

PROXY_URL = os.environ.get("PROXY_URL")

# ─── قاموس: إنجليزي ← عربي ───
WORDS = {
    # أنواع الملابس
    "dress": "فستان", "frock": "فستان", "gown": "فستان سهرة",
    "shirt": "قميص", "blouse": "بلوزة", "top": "توب",
    "t-shirt": "تيشيرت", "t shirt": "تيشيرت", "tee": "تيشيرت",
    "hoodie": "هودي", "sweatshirt": "سويت شيرت",
    "jacket": "جاكيت", "coat": "معطف", "blazer": "بليزر",
    "cardigan": "كارديجان", "sweater": "سترة", "pullover": "بلوفر",
    "pants": "بنطلون", "trousers": "بنطلون", "jeans": "جينز",
    "chinos": "شينو", "shorts": "شورت", "skirt": "تنورة",
    "leggings": "ليقنز", "jumpsuit": "جمبسوت", "romper": "رومبر",
    "bodysuit": "بدي", "overalls": "أوفرول",
    "socks": "جوارب", "tights": "جورب شفاف", "stockings": "شرابات",
    "pajamas": "بيجاما", "pyjamas": "بيجاما", "nightwear": "لبس نوم",
    "lingerie": "لانجري", "bra": "صدرية", "underwear": "ملابس داخلية",
    "bedsheet": "مفرش", "bedding": "مفرش", "duvet": "مفرش", "quilt": "مفرش",
    
    # أحذية
    "shoes": "حذاء", "sneakers": "سنيكرز", "trainers": "حذاء رياضي",
    "boots": "بوت", "ankle boots": "بوت كاحل", "sandals": "صندل",
    "slippers": "شبشب", "heels": "كعب عالي", "pumps": "كعب",
    "flats": "باليرينا", "loafers": "لوفر", "oxfords": "أوكسفورد",
    
    # شنط وإكسسوارات
    "bag": "شنطة", "handbag": "شنطة يد", "backpack": "شنطة ظهر",
    "tote": "توت باج", "clutch": "كلتش", "crossbody": "كروس بودي",
    "wallet": "محفظة", "belt": "حزام", "tie": "ربطة عنق",
    "scarf": "وشاح", "gloves": "قفازات", "hat": "قبعة", "cap": "كاب",
    "sunglasses": "نظارة شمسية", "watch": "ساعة",
    "jewelry": "مجوهرات", "necklace": "عقد", "bracelet": "سوار",
    "ring": "خاتم", "earrings": "حلق", "earring": "حلق", "mirror": "مرآة",
    
    # عناية ومكياج
    "perfume": "عطر", "fragrance": "عطر", "cologne": "كولونيا",
    "makeup": "مكياج", "lipstick": "أحمر شفاه", "lip gloss": "ملمع شفاه",
    "foundation": "كريم أساس", "mascara": "ماسكارا",
    "eyeliner": "آيلاينر", "eyeshadow": "ظل عيون",
    "blush": "بلاشر", "highlighter": "هايلايتر", "concealer": "كونسيلر",
    "primer": "برايمر", "setting spray": "مثبت مكياج",
    "cream": "كريم", "lotion": "لوشن", "serum": "سيروم",
    "toner": "تونر", "moisturizer": "مرطب", "sunscreen": "واقي شمس",
    "shampoo": "شامبو", "conditioner": "بلسم", "mask": "ماسك",
    "soap": "صابون", "brush": "فرشاة",
    
    # خامات
    "denim": "جينز", "leather": "جلد", "suede": "شمواه",
    "velvet": "مخمل", "satin": "ساتان", "silk": "حرير",
    "cotton": "قطن", "linen": "كتان", "wool": "صوف",
    "knit": "محبوك", "knitted": "محبوك", "mesh": "شبك", "lace": "دانتيل",
    "chiffon": "شيفون", "organza": "أورجانزا", "sequin": "ترتر",
    
    # ألوان
    "black": "أسود", "white": "أبيض", "red": "أحمر", "blue": "أزرق",
    "green": "أخضر", "yellow": "أصفر", "pink": "وردي", "purple": "بنفسجي",
    "orange": "برتقالي", "brown": "بني", "beige": "بيج", "grey": "رمادي",
    "gray": "رمادي", "navy": "كحلي", "burgundy": "عنابي", "maroon": "عنابي",
    "olive": "زيتي", "khaki": "كاكي", "cream": "كريمي", "ivory": "عاجي",
    "gold": "ذهبي", "silver": "فضي", "rose gold": "روز جولد",
    "multicolor": "ملون", "colorful": "ملون",
    "printed": "مطبوع", "floral": "زهري", "striped": "مخطط",
    "checked": "كاروهات", "plaid": "كاروهات", "polka dot": "منقط",
    
    # عدد القطع
    "set": "طقم", "pack": "طقم", "bundle": "طقم",
}

SKIP_WORDS = {
    "shein", "for", "with", "and", "the", "a", "an", "in", "on", "at", "to", "of",
    "by", "from", "up", "out", "new", "hot", "sale", "best", "top", "fashion",
    "style", "look", "trend", "collection", "brand", "designer", "premium",
    "quality", "cheap", "affordable", "luxury", "exclusive", "limited",
    "edition", "season", "spring", "summer", "autumn", "fall", "winter",
    "2023", "2024", "2025", "2026", "x", "xl", "xxl", "s", "m", "l", "xs", "xxxl", 
    "one size", "plus size", "size", "cm", "mm", "inch", "usd", "sar", "off", "discount",
    "office", "travel", "sexy", "pure", "group", "beauty", "color", "sizing", "com"
}

TYPE_SET = set(WORDS.values())

FEMALE_ONLY_TYPES = {
    "فستان", "فستان سهرة", "بلوزة", "تنورة", "كعب عالي", "كعب", "باليرينا", 
    "شنطة يد", "كلتش", "توت باج", "كروس بودي", "بلاشر", "أحمر شفاه", "ملمع شفاه", 
    "ماسكارا", "آيلاينر", "ظل عيون", "هايلايتر", "كونسيلر", "برايمر", "مثبت مكياج", 
    "رومبر", "بدي", "جمبسوت", "بيجاما", "لبس نوم", "لانجري", "صدرية", "ملابس داخلية", "مفرش"
}

BEAUTY_TYPES = {
    "مكياج", "أحمر شفاه", "ملمع شفاه", "كريم أساس", "ماسكارا", "آيلاينر", 
    "ظل عيون", "بلاشر", "هايلايتر", "كونسيلر", "برايمر", "مثبت مكياج", 
    "كريم", "لوشن", "سيروم", "تونر", "مرطب", "واقي شمس", "شامبو", "بلسم", "ماسك", "صابون", "فرشاة"
}


def extract_keywords(title):
    clean = title.lower()
    clean = re.sub(r'com\.\w+', '', clean)
    clean = re.sub(r'[^\w\s\-]', ' ', clean)
    clean = re.sub(r'\s+', ' ', clean).strip()
    words = clean.split()
    
    found = []
    i = 0
    while i < len(words):
        if words[i] in SKIP_WORDS:
            i += 1
            continue
        if i + 1 < len(words):
            two = f"{words[i]} {words[i+1]}"
            if two in WORDS:
                found.append(WORDS[two])
                i += 2
                continue
        w = words[i]
        if w in WORDS:
            found.append(WORDS[w])
        i += 1
    return found


def build_description(title):
    kw = extract_keywords(title)
    types = [k for k in kw if k in TYPE_SET]
    main_type = max(types, key=len) if types else ""

    # 1. صياغات للمكياج والعناية بالبشرة
    if main_type in BEAUTY_TYPES:
        templates = [
            "بناااااات أكثررر ميزة لاحظتها فيها ✨\n\nتخلي الجسسسسم يبرق ويرعد نضاااارة 😩🤍",
            "مرررره عجبنيييي بنات 🤎\n\nوالأحلى إنها استخدمته بأكثر من طريقة! 👌🏻\nألوانه صبااااحية وناعمة تنفع للاستخدام اليومي بدون تفكير 🤎☕️",
            "بنااات هالمنتج خيااالي للنضارة واللمعة ناعم ومكانه أساسي بالروتين ✨🧴"
        ]
        return random.choice(templates)

    # 2. صياغات المفارش والمستلزمات
    elif main_type == "مفرش":
        templates = [
            "عرووووسة وتبغين مفرش لجهازك؟ 👰🏻‍♀️\nحقيقي مفرش عروووسة بكل ما تعنيه الكلمة!",
            "بنااات المفرررش يفتح النفس كأنه مفرش فنادق فخم وناعم مررره ✨🤍"
        ]
        return random.choice(templates)

    # 3. صياغات الملابس والتنسيقات الأنثوية
    else:
        if main_type in ["توب", "بلوزة", "بدي"]:
            templates = [
                "دايم أحببب التوبات اللي كذا 🤍\n\nتنلبس كطقم أو تدخل مع تنسيقات ثانية بكل سهولة ✨",
                "القططططع اللي كذا تخدمكم وقت الدوامااات خصوصًا تحت الأقمصة✨"
            ]
            return random.choice(templates)
        elif main_type in ["قميص", "جاكيت", "بليزر", "بنطلون"]:
            templates = [
                "رهييييبة للدوامااات وللصييف ☀️\n\nخفيفة ومرتبة وتخدمكم كثيييير بالتنسيقات اليومية✨",
                "القططططع اللي كذا تخدمكم وقت الدوامااات مرتبة وشيك✨"
            ]
            return random.choice(templates)
        else:
            templates = [
                "أحببب القطع الأنثوووية اللي كذا 🥹\nألوااانها رايييييقة وناعمة بشكل ✨",
                "موديلها غرييييب بس حللللووو وتغييررر! \n\nخصوصًا للي يحبون القطع المختلفة والستايل اللي مو مكرر 🤌🏻",
                "شوفوا الأنوقاااه يا بنات! القطعة تجننن باللبس وطلتها تاخد العقل 💕✨"
            ]
            return random.choice(templates)


def is_shein_url(url):
    return "shein.com" in url.lower() or "onelink.shein.com" in url.lower() or "ty.gl" in url.lower()


def get_shein_product(url):
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    ]

    for attempt, ua in enumerate(user_agents):
        try:
            delay = (2 ** attempt) + random.uniform(0.5, 1.5)
            if attempt > 0:
                time.sleep(delay)

            session = requests.Session()
            headers = {
                "User-Agent": ua,
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }

            proxies = {"http": PROXY_URL, "https": PROXY_URL} if PROXY_URL else {}
            r = session.get(url, headers=headers, timeout=15, proxies=proxies, allow_redirects=True)

            if r.status_code != 200 or len(r.text) < 3000:
                continue

            soup = BeautifulSoup(r.text, "html.parser")

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

            if not title:
                title = "منتج مميز"

            return {
                "full_title": title,
                "image": image,
            }

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            continue

    return {"full_title": "منتج مميز", "image": None}


@bot.message_handler(func=lambda m: True)
def handler(msg):
    text = msg.text.strip()
    urls = re.findall(r"https?://\S+", text)

    if not urls:
        bot.reply_to(msg, "❌ يرجى إرسال رابط المنتج")
        return

    for original_url in urls:
        wait = bot.reply_to(msg, "⏳ جاري استخراج البيانات...")

        product = get_shein_product(original_url)

        product_caption = build_description(product["full_title"])
        post = f"{product_caption}\n\n🔗 {original_url}"

        try:
            if product.get("image"):
                bot.send_photo(msg.chat.id, product["image"], caption=post)
            else:
                bot.send_message(msg.chat.id, post)
            bot.delete_message(msg.chat.id, wait.message_id)
        except Exception as e:
            print(f"Error sending: {e}")
            try:
                bot.send_message(msg.chat.id, post)
                bot.delete_message(msg.chat.id, wait.message_id)
            except Exception as e2:
                bot.edit_message_text("❌ حدث خطأ في الإرسال", msg.chat.id, wait.message_id)


app = Flask(__name__)

WEBHOOK_HOST = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
WEBHOOK_PORT = int(os.environ.get("PORT", 10000))
WEBHOOK_URL_BASE = f"https://{WEBHOOK_HOST}" if WEBHOOK_HOST else None
WEBHOOK_URL_PATH = f"/webhook/{TOKEN}"

@app.route("/")
def index():
    return "🤖 البوت يعمل"

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
