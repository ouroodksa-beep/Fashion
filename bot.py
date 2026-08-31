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
    
    # قصات وتفاصيل
    "slim fit": "ضيق", "regular fit": "عادي", "loose fit": "واسع",
    "oversized": "أوفرسايز", "skinny": "سكيني", "straight": "مستقيم",
    "wide leg": "رجل واسعة", "cropped": "قصير", "crop": "قصير",
    "mini": "ميني", "midi": "ميدي", "maxi": "ماكسي",
    "ruched": "مكشكش", "pleated": "مطوي", "ruffle": "كشكشة",
    "embroidered": "مطرز", "v-neck": "رقبة V", "round neck": "رقبة دائرية",
    "long sleeve": "أكمام طويلة", "short sleeve": "أكمام قصيرة",
    "sleeveless": "بدون أكمام", "puff sleeve": "أكمام منفوخة",
    
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

TYPE_SET = {"فستان", "فستان سهرة", "قميص", "بلوزة", "توب", "تيشيرت", "هودي",
            "سويت شيرت", "جاكيت", "معطف", "بليزر", "كارديجان", "سترة", "بلوفر",
            "بنطلون", "جينز", "شينو", "شورت", "تنورة", "ليقنز", "جمبسوت", "رومبر",
            "بدي", "أوفرول", "بيجاما", "لبس نوم", "لانجري", "صدرية", "ملابس داخلية",
            "حذاء", "سنيكرز", "صندل", "كعب عالي", "كعب", "باليرينا",
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
             "كريمي", "عاجي", "ذهبي", "فضي", "روز جولد", "ملون", "مطبوع", "زهري", "مخطط", "كاروهات", "منقط"}

MATERIAL_SET = {"جينز", "جلد", "شمواه", "مخمل", "ساتان", "حرير", "قطن", "كتان", "صوف", "محبوك", "شبك", "دانتيل", "شيفون", "أورجانزا", "ترتر"}

EMOJI_MAP = {
    "فستان": "👗", "فستان سهرة": "✨", "قميص": "👔", "بلوزة": "👚", "توب": "👕",
    "تيشيرت": "👕", "هودي": "🧥", "سويت شيرت": "🧥", "جاكيت": "🧥", "معطف": "🧥",
    "بليزر": "🤵", "كارديجان": "🧶", "سترة": "🧶", "بلوفر": "🧶", "بنطلون": "👖", 
    "جينز": "👖", "شورت": "🩳", "تنورة": "👗", "ليقنز": "🖤", "جمبسوت": "👗", 
    "رومبر": "👗", "بدي": "👙", "بيجاما": "🌙", "لبس نوم": "🌙", "لانجري": "💋", 
    "حذاء": "👞", "سنيكرز": "👟", "صندل": "🩴", "كعب عالي": "👠", "كعب": "👠",
    "باليرينا": "🥿", "بوت": "👢", "شبشب": "🩴", "شنطة": "👜", "شنطة يد": "👜", 
    "شنطة ظهر": "🎒", "توت باج": "🛍️", "كلتش": "👝", "كروس بودي": "👜", "محفظة": "👛", 
    "نظارة شمسية": "🕶️", "ساعة": "⌚", "مجوهرات": "💎", "عقد": "📿", "حلق": "💎", 
    "عطر": "🌸", "مكياج": "💄", "أحمر شفاه": "💋", "كريم": "🧴", "مرطب": "🧴"
}


def extract_quantity(title):
    t = title.lower()
    patterns = [
        r'(\d+)\s*(?:pc|pcs|piece|pieces)\b',
        r'(\d+)\s*-\s*(?:pc|pcs|piece|pieces)\b',
        r'\b(?:set|pack|bundle)\s+of\s+(\d+)',
        r'\b(\d+)\s*(?:set|pack|bundle)\b',
    ]
    for pat in patterns:
        m = re.search(pat, t)
        if m:
            n = int(m.group(1))
            if n > 1:
                return f"{n} قطع"
    if re.search(r'\b(?:set|pack|bundle)\b', t):
        return "طقم"
    return None


def detect_gender(title):
    t = title.lower()
    if any(w in t for w in ["kids", "children", "child", "baby", "toddler", "infant", "girls'", "boy's"]):
        return "أطفال"
    if any(w in t for w in ["men", "man", "male", "mens", "men's", "boys'"]):
        return "رجالي"
    return "نسائي"


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
    colors = [k for k in kw if k in COLOR_SET]
    materials = [k for k in kw if k in MATERIAL_SET]
    
    main_type = max(types, key=len) if types else ""
    quantity = extract_quantity(title)
    gender = detect_gender(title)
    
    color = colors[0] if colors else ""
    material = materials[0] if materials else ""
    emoji = EMOJI_MAP.get(main_type, "✨")
    
    desc_elements = []
    if quantity: desc_elements.append(f"({quantity})")
    if color: desc_elements.append(f"لون {color}")
    if material: desc_elements.append(f"خامة {material}")
    
    detail_str = " - ".join(desc_elements)
    
    # ─── صياغة النصوص بدقة متناهية ───
    if gender == "أطفال":
        item_word = f"الـ {main_type}" if main_type else "القطعة"
        phrase = f"يا عيني على الكيوت! شوفوا {item_word} للأطفال تجنن باللبس 👶{emoji}"
    elif gender == "رجالي":
        item_word = f"الـ {main_type}" if main_type else "هذا المنتج"
        phrase = f"للشباب.. شوفوا {item_word} ترتيب وشياكة مو عادية 🔥{emoji}"
    else:  # نسائي
        if main_type:
            intros = [
                f"يا بنات شوفوا هذا الـ {main_type} يجنن وأناقة مو عادية! 😍{emoji}",
                f"بنات الحقوا على هذا الـ {main_type} خيالي باللبس وطلته تاخد العقل 💕{emoji}",
                f"شوفوا الروعة يا بنات! {main_type} شيك ومرتب بشكل مو عادي 🔥{emoji}"
            ]
        else:
            intros = [
                f"يا بنات شوفوا هذه القطعة تجنن وأناقتها مو عادية! 😍✨",
                f"بنات شوفوا هذه القطعة الخيالية باللبس، طلتها تاخد العقل 💕✨"
            ]
        phrase = random.choice(intros)
    
    # الخاتمة شيك وبدون "قبل ينفد"
    closings = [
        "تسوقوا الآن من الرابط التالي 🛒✨",
        "لطلب المنتج واستعراض التفاصيل 👇🛍️",
        "رابط الطلب المباشر ✨🛒"
    ]
    selected_closing = random.choice(closings)
    
    if detail_str:
        final_text = f"{phrase}\n📌 التفاصيل: {detail_str}\n\n{selected_closing}"
    else:
        final_text = f"{phrase}\n\n{selected_closing}"
        
    return final_text


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

        product_caption = build_description(product["full_title"])
        post = f"{product_caption}\n🔗 {original_url}"

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
