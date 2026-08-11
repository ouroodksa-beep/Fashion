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
    "multicolor": "متعدد الألوان", "colorful": "متعدد الألوان",
    "printed": "مطبوع", "floral": "زهري", "striped": "مخطط",
    "checked": "كاروهات", "plaid": "كاروهات", "polka dot": "منقط",
    "solid": "سادة", "plain": "سادة",
    
    # قصات وأنماط
    "slim fit": "ضيق", "regular fit": "عادي", "loose fit": "واسع",
    "oversized": "واسع", "skinny": "سكيني", "straight": "مستقيم",
    "wide leg": "رجل واسعة", "flare": "منفوش", "cropped": "قصير", 
    "crop": "قصير", "mini": "ميني", "midi": "ميدي", "maxi": "ماكسي",
    "high waist": "خصر عالي", "low waist": "خصر منخفض",
    "loose": "واسع",
    
    # تفاصيل
    "ruched": "مكشكش", "pleated": "مطوي", "ruffle": "كشكشة",
    "embroidered": "مطرز", "zipper": "سحاب", "button": "أزرار",
    "v-neck": "رقبة V", "v neck": "رقبة V", "round neck": "رقبة دائرية",
    "polo neck": "رقبة بولو", "polo": "بولو",
    "long sleeve": "أكمام طويلة", "short sleeve": "أكمام قصيرة",
    "sleeveless": "بلا أكمام", "puff sleeve": "أكمام منفوخة",
    "boho": "بوهيمي", "casual": "كاجوال",
    
    # عدد القطع
    "set": "طقم", "pack": "طقم", "bundle": "طقم",
}

SKIP_WORDS = {
    "shein", "for", "with", "and", "the", "a", "an", "in", "on", "at", "to", "of",
    "by", "from", "up", "out", "new", "hot", "sale", "best", "top", "fashion",
    "style", "look", "trend", "collection", "brand", "designer", "premium",
    "quality", "cheap", "affordable", "luxury", "exclusive", "limited",
    "edition", "season", "spring", "summer", "autumn", "fall", "winter",
    "2023", "2024", "2025", "2026",
    "x", "xl", "xxl", "s", "m", "l", "xs", "xxxl", "one size",
    "plus size", "size", "cm", "mm", "inch", "inches", "ml", "g", "kg",
    "usd", "eur", "gbp", "sar", "aed", "qar", "kwd", "egp", "off", "discount",
    "office", "travel", "sexy", "pure", "group", "beauty", "color", "sizing",
    "sephora", "joocyee", "com", "false", "patchwork", "slouchy", "ribbed",
    "مكتب", "سفر", "يسافر", "جنسي", "نقي", "جماعية", "جمال", "لون", "تحجيم",
    "خليط", "زائف", "مترهل", "مضلع", "رائع", "هالة", "منفوش"
}

# ─── التصنيفات ───
TYPE_SET = {"فستان", "فستان سهرة", "قميص", "بلوزة", "توب", "تيشيرت", "هودي",
            "سويت شيرت", "جاكيت", "معطف", "بليزر", "كارديجان", "سترة", "بلوفر",
            "بنطلون", "جينز", "شينو", "شورت", "تنورة", "ليقنز", "جمبسوت", "رومبر",
            "بدي", "أوفرول", "حذاء", "سنيكرز", "صندل", "كعب عالي", "كعب", "باليرينا",
            "لوفر", "أوكسفورد", "بوت", "بوت كاحل", "شبشب", "حذاء رياضي",
            "شنطة", "شنطة يد", "شنطة ظهر", "توت باج", "كلتش", "كروس بودي",
            "محفظة", "حزام", "ربطة عنق", "وشاح", "قفازات", "قبعة", "كاب",
            "نظارة شمسية", "ساعة", "مجوهرات", "عقد", "سوار", "خاتم", "حلق", "مرآة",
            "عطر", "كولونيا", "مكياج", "أحمر شفاه", "ملمع شفاه", "كريم أساس",
            "ماسكارا", "آيلاينر", "ظل عيون", "بلاشر", "هايلايتر", "كونسيلر",
            "برايمر", "مثبت مكياج", "كريم", "لوشن", "سيروم", "تونر", "مرطب",
            "واقي شمس", "شامبو", "بلسم", "ماسك", "صابون", "فرشاة",
            "جوارب", "جورب شفاف", "شرابات"}

COLOR_SET = {"أسود", "أبيض", "أحمر", "أزرق", "أخضر", "أصفر", "وردي", "بنفسجي",
             "برتقالي", "بني", "بيج", "رمادي", "كحلي", "عنابي", "زيتي", "كاكي",
             "كريمي", "عاجي", "ذهبي", "فضي", "روز جولد", "متعدد الألوان", "سادة",
             "مطبوع", "زهري", "مخطط", "كاروهات", "منقط"}

MATERIAL_SET = {"جينز", "جلد", "شمواه", "مخمل", "ساتان", "حرير", "قطن", "كتان",
                "صوف", "محبوك", "شبك", "دانتيل", "شيفون", "أورجانزا", "ترتر"}

FIT_SET = {"ضيق", "عادي", "واسع", "سكيني", "مستقيم", "رجل واسعة", "منفوش", "قصير",
           "ميني", "ميدي", "ماكسي", "خصر عالي", "خصر منخفض"}

NECK_SET = {"رقبة V", "رقبة دائرية", "رقبة بولو", "بولو"}
SLEEVE_SET = {"أكمام طويلة", "أكمام قصيرة", "بلا أكمام", "أكمام منفوخة"}
DETAIL_SET = {"مكشكش", "مطوي", "كشكشة", "مطرز", "سحاب", "أزرار", "بوهيمي", "كاجوال"}

BOTTOM_SET = {"بنطلون", "جينز", "شينو", "شورت", "تنورة", "ليقنز"}
SHOE_SET = {"حذاء", "سنيكرز", "صندل", "كعب عالي", "كعب", "باليرينا", "لوفر", "أوكسفورد", "بوت", "بوت كاحل", "شبشب", "حذاء رياضي"}
ACCESSORY_SET = {"شنطة", "شنطة يد", "شنطة ظهر", "توت باج", "كلتش", "كروس بودي", "محفظة", "حزام", "ربطة عنق", "وشاح", "قفازات", "قبعة", "كاب", "نظارة شمسية", "ساعة", "مجوهرات", "عقد", "سوار", "خاتم", "حلق", "مرآة"}
BEAUTY_SET = {"عطر", "كولونيا", "مكياج", "أحمر شفاه", "ملمع شفاه", "كريم أساس", "ماسكارا", "آيلاينر", "ظل عيون", "بلاشر", "هايلايتر", "كونسيلر", "برايمر", "مثبت مكياج", "كريم", "لوشن", "سيروم", "تونر", "مرطب", "واقي شمس", "شامبو", "بلسم", "ماسك", "صابون", "فرشاة"}

EMOJI_MAP = {
    "فستان": "👗", "فستان سهرة": "✨", "قميص": "👔", "بلوزة": "👚", "توب": "👕",
    "تيشيرت": "👕", "هودي": "🧥", "سويت شيرت": "🧥", "جاكيت": "🧥", "معطف": "🧥",
    "بليزر": "🤵", "كارديجان": "🧶", "سترة": "🧶", "بلوفر": "🧶",
    "بنطلون": "👖", "جينز": "👖", "شينو": "👖", "شورت": "🩳", "تنورة": "👗",
    "ليقنز": "🖤", "جمبسوت": "👗", "رومبر": "👗", "بدي": "👙", "أوفرول": "👖",
    "حذاء": "👞", "سنيكرز": "👟", "صندل": "🩴", "كعب عالي": "👠", "كعب": "👠",
    "باليرينا": "🥿", "لوفر": "👞", "أوكسفورد": "👞", "بوت": "👢", "بوت كاحل": "👢",
    "شبشب": "🩴", "حذاء رياضي": "👟",
    "شنطة": "👜", "شنطة يد": "👜", "شنطة ظهر": "🎒", "توت باج": "🛍️", "كلتش": "👝",
    "كروس بودي": "👜", "محفظة": "👛", "حزام": "🖤", "ربطة عنق": "👔", "وشاح": "🧣",
    "قفازات": "🧤", "قبعة": "🎩", "كاب": "🧢", "نظارة شمسية": "🕶️", "ساعة": "⌚",
    "مجوهرات": "💎", "عقد": "📿", "سوار": "📿", "خاتم": "💍", "حلق": "💎", "مرآة": "🪞",
    "عطر": "🌸", "كولونيا": "🌸", "مكياج": "💄", "أحمر شفاه": "💋", "ملمع شفاه": "💋",
    "كريم أساس": "💄", "ماسكارا": "👁️", "آيلاينر": "👁️", "ظل عيون": "👁️",
    "بلاشر": "🌸", "هايلايتر": "✨", "كونسيلر": "💄", "برايمر": "💄",
    "مثبت مكياج": "💨", "كريم": "🧴", "لوشن": "🧴", "سيروم": "🧴", "تونر": "🧴",
    "مرطب": "🧴", "واقي شمس": "☀️", "شامبو": "🧴", "بلسم": "🧴", "ماسك": "🧖‍♀️",
    "صابون": "🧼", "فرشاة": "🖌️",
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
        if i + 2 < len(words):
            three = f"{words[i]} {words[i+1]} {words[i+2]}"
            if three in WORDS:
                found.append(WORDS[three])
                i += 3
                continue
        if i + 1 < len(words):
            two = f"{words[i]} {words[i+1]}"
            if two in WORDS:
                found.append(WORDS[two])
                i += 2
                continue
            two_dash = f"{words[i]}-{words[i+1]}"
            if two_dash in WORDS:
                found.append(WORDS[two_dash])
                i += 2
                continue
        w = words[i]
        if w in WORDS:
            found.append(WORDS[w])
        i += 1
    return found


def build_description(title):
    kw = extract_keywords(title)
    if not kw:
        return "منتج مميز ✨"
    
    types = [k for k in kw if k in TYPE_SET]
    colors = [k for k in kw if k in COLOR_SET]
    materials = [k for k in kw if k in MATERIAL_SET]
    fits = [k for k in kw if k in FIT_SET]
    necks = [k for k in kw if k in NECK_SET]
    sleeves = [k for k in kw if k in SLEEVE_SET]
    details = [k for k in kw if k in DETAIL_SET]
    
    main_type = max(types, key=len) if types else ""
    
    is_bottom = main_type in BOTTOM_SET
    is_shoe = main_type in SHOE_SET
    is_acc = main_type in ACCESSORY_SET
    is_beauty = main_type in BEAUTY_SET
    
    # فلترة منطقية
    if is_bottom:
        sleeves = []
        necks = []
    if is_shoe or is_acc or is_beauty:
        sleeves = []
        necks = []
        fits = [f for f in fits if f not in {"قصير", "ميني", "ميدي", "ماكسي", "خصر عالي", "خصر منخفض"}]
    if is_acc or is_beauty:
        fits = []
    
    # احذف "سادة" تماماً
    colors = [c for c in colors if c != "سادة"]
    
    # احذف "كاجوال" و"عادي" تماماً (مفروضات)
    details = [d for d in details if d not in {"كاجوال", "عادي"}]
    fits = [f for f in fits if f != "عادي"]
    
    color = colors[0] if colors else ""
    material = materials[0] if materials else ""
    fit = fits[0] if fits else ""
    neck = necks[0] if necks else ""
    sleeve = sleeves[0] if sleeves else ""
    detail = details[0] if details else ""
    
    # منع التكرار: الخامة = النوع
    if material == main_type:
        material = ""
    
    # ─── بناء الجملة بالقالب الثابت ───
    # [النوع] [الفيت] [اللون] [الخامة] | [التفاصيل]
    
    parts = []
    if main_type:  parts.append(main_type)
    if fit:        parts.append(fit)
    if color:      parts.append(color)
    if material:   parts.append(material)
    
    headline = " ".join(parts)
    
    # التفاصيل
    extras = []
    if neck:    extras.append(neck)
    if sleeve:  extras.append(sleeve)
    if detail:  extras.append(detail)
    if len(details) > 1:
        extras.append(details[1])
    extras = list(dict.fromkeys(extras))
    
    emoji = EMOJI_MAP.get(main_type, "✨")
    
    if extras:
        extra_str = " و".join(extras)
        desc = f"{headline} {emoji} | {extra_str}"
    else:
        desc = f"{headline} {emoji}"
    
    return re.sub(r'\s+', ' ', desc).strip()


def is_shein_url(url):
    return "shein.com" in url.lower() or "onelink.shein.com" in url.lower()


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
                continue

            return {
                "full_title": title,
                "image": image,
            }

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            continue

    return None


@bot.message_handler(func=lambda m: True)
def handler(msg):
    text = msg.text.strip()
    urls = re.findall(r"https?://\S+", text)

    if not urls:
        bot.reply_to(msg, "❌ يرجى إرسال رابط المنتج من شي إن")
        return

    for original_url in urls:
        if not is_shein_url(original_url):
            bot.reply_to(msg, "❌ الرابط يجب أن يكون من shein.com")
            continue

        wait = bot.reply_to(msg, "⏳ جاري استخراج البيانات...")

        product = get_shein_product(original_url)

        if not product:
            bot.edit_message_text("❌ تعذر قراءة بيانات المنتج", msg.chat.id, wait.message_id)
            continue

        product_name = build_description(product["full_title"])
        post = f"{product_name}\n\n{original_url}"

        try:
            if product["image"]:
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
