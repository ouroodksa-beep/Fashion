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

# ─── قاموس شامل ومعدل: إنجليزي ← عربي ───
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
    "checked": "مربعات", "plaid": "مربعات", "polka dot": "منقط",
    "solid": "سادة", "plain": "سادة",
    
    # قصات وأنماط
    "slim fit": "ضيق", "regular fit": "عادي", "loose fit": "واسع",
    "oversized": "واسع", "skinny": "سكيني", "straight": "مستقيم",
    "wide leg": "رجل واسعة", "flare": "منفوش", "cropped": "قصير", 
    "crop": "قصير", "mini": "ميني", "midi": "ميدي", "maxi": "ماكسي",
    "high waist": "خصر عالي", "low waist": "خصر منخفض",
    
    # تفاصيل
    "ruched": "مكشكش", "pleated": "مطوي", "ruffle": "كشكشة",
    "embroidered": "مطرز", "zipper": "سحاب", "button": "أزرار",
    "v-neck": "رقبة V", "v neck": "رقبة V", "round neck": "رقبة دائرية",
    "polo neck": "رقبة بولو", "polo": "بولو",
    "long sleeve": "أكمام طويلة", "short sleeve": "أكمام قصيرة",
    "sleeveless": "بلا أكمام", "puff sleeve": "أكمام منفوخة",
    "boho": "بوهيمي", "casual": "كاجوال",
}

# كلمات حشو وترجمات عشوائية يتم حذفها تماماً
SKIP_WORDS = {
    "shein", "for", "with", "and", "the", "a", "an", "in", "on", "at", "to", "of",
    "by", "from", "up", "out", "new", "hot", "sale", "best", "top", "fashion",
    "style", "look", "trend", "collection", "brand", "designer", "premium",
    "quality", "cheap", "affordable", "luxury", "exclusive", "limited",
    "edition", "season", "spring", "summer", "autumn", "fall", "winter",
    "2023", "2024", "2025", "2026", "pcs", "pc", "pack", "set", "piece",
    "pieces", "x", "xl", "xxl", "s", "m", "l", "xs", "xxxl", "one size",
    "plus size", "size", "cm", "mm", "inch", "inches", "ml", "g", "kg",
    "usd", "eur", "gbp", "sar", "aed", "qar", "kwd", "egp", "off", "discount",
    "office", "travel", "sexy", "pure", "group", "beauty", "color", "sizing",
    "sephora", "joocyee", "com", "false", "patchwork", "slouchy", "ribbed",
    "مكتب", "سفر", "يسافر", "جنسي", "نقي", "جماعية", "جمال", "لون", "تحجيم",
    "خليط", "زائف", "مترهل", "مضلع", "رائع", "هالة", "منفوش"
}

GENDER_MARKERS = {
    "women", "woman", "ladies", "lady", "female", "womens", "women's",
    "men", "man", "male", "mens", "men's", "gentleman", "gentlemen",
    "girls", "girl", "boys", "boy", "kids", "children", "child",
    "baby", "toddler", "infant", "newborn", "youth", "teen",
}


def detect_gender(title):
    title_lower = title.lower()
    has_female = any(w in title_lower for w in ["women", "woman", "ladies", "lady", "female", "womens", "women's", "girl's", "girls'", "dress", "skirt", "blouse", "heels", "handbag", "blush", "lipstick"])
    has_male = any(w in title_lower for w in ["men", "man", "male", "mens", "men's", "boy's", "boys'", "suit", "tuxedo", "chinos"])
    has_kids = any(w in title_lower for w in ["kids", "children", "child", "baby", "toddler", "infant", "newborn"])
    
    if has_kids:
        return "أطفال"
    if has_female and not has_male:
        return "نسائي"
    if has_male and not has_female:
        return "رجالي"
    return ""


def extract_keywords(title):
    clean = title.lower()
    # تنظيف الروابط أو com.
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
    gender = detect_gender(title)
    keywords = extract_keywords(title)
    
    if not keywords:
        return "منتج مميز من شي إن"
    
    # تصنيف الكلمات لإعادة ترتيبها بشكل صحيح
    type_keywords = {"فستان", "فستان سهرة", "قميص", "بلوزة", "توب", "تيشيرت", "هودي", "سويت شيرت", "جاكيت", "معطف", "بليزر", "كارديجان", "سترة", "بلوفر", "بنطلون", "جينز", "شورت", "تنورة", "ليقنز", " جمبسوت", "حذاء", "سنيكرز", "صندل", "كعب عالي", "كعب", "شنطة", "شنطة يد", "مرآة", "عطر", "مكياج", "أحمر شفاه", "ملمع شفاه", "كريم أساس", "ماسكارا", "بلاشر", "هايلايتر", "سيروم", "مرطب"}
    color_keywords = {"أسود", "أبيض", "أحمر", "أزرق", "أخضر", "أصفر", "وردي", "بنفسجي", "برتقالي", "بني", "بيج", "رمادي", "كحلي", "عنابي", "زيتي", "ذهبي", "فضي", "سادة", "مطبوع", "زهري", "مخطط", "مربعات"}
    material_keywords = {"جينز", "جلد", "شمواه", "مخمل", "ساتان", "حرير", "قطن", "كتان", "صوف", "محبوك", "دانتيل", "شيفون", "ترتر"}
    
    types = [k for k in keywords if k in type_keywords]
    colors = [k for k in keywords if k in color_keywords]
    materials = [k for k in keywords if k in material_keywords]
    details = [k for k in keywords if k not in type_keywords and k not in color_keywords and k not in material_keywords]
    
    # إزالة التكرار
    details = list(dict.fromkeys(details))
    
    # بناء الجملة: [نوع المنتج] + [الجنس] + [اللون] + [الخامة] + [بقية التفاصيل]
    parts = []
    
    if types:
        parts.append(types[-1]) # أخذ نوع المنتج الأساسي
    else:
        parts.append("قطعة")
        
    if gender:
        parts.append(gender)
        
    if colors:
        parts.append(colors[0])
        
    if materials:
        parts.append(materials[0])
        
    if details:
        parts.extend(details[:3]) # أخذ أول 3 تفاصيل مهمة فقط
        
    result = " ".join(parts)
    return re.sub(r'\s+', ' ', result).strip()


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
                "Accept-Language": "en-US,en;q=0.9", # جلب العنوان بالإنجليزي لمعالجته بدقة
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

        # بناء اسم منتج مفهوم ومترجم صح
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
    # شنط وإكسسوارات
    "bag": "شنطة", "handbag": "شنطة يد", "backpack": "شنطة ظهر",
    "tote": "توت باج", "clutch": "كلتش", "crossbody": "كروس بودي",
    "wallet": "محفظة", "belt": "حزام", "tie": "ربطة عنق",
    "scarf": "وشاح", "gloves": "قفازات", "hat": "قبعة", "cap": "كاب",
    "sunglasses": "نظارة شمسية", "watch": "ساعة",
    "jewelry": "مجوهرات", "necklace": "عقد", "bracelet": "سوار",
    "ring": "خاتم", "earrings": "حلق", "earring": "حلق",
    
    # عناية
    "perfume": "عطر", "fragrance": "عطر", "cologne": "كولونيا",
    "makeup": "ميك أب", "lipstick": "أحمر شفاه", "lip gloss": "لمع شفاه",
    "foundation": "كريم أساس", "mascara": "ماسكارا",
    "eyeliner": "آيلاينر", "eyeshadow": "ظل عيون",
    "blush": "بلاشر", "highlighter": "هايلايتر", "concealer": "كونسيلر",
    "primer": "برايمر", "setting spray": "فيكس سبري",
    "cream": "كريم", "lotion": "لوشن", "serum": "سيروم",
    "toner": "تونر", "moisturizer": "مرطب", "sunscreen": "واقي شمس",
    "shampoo": "شامبو", "conditioner": "بلسم", "mask": "ماسك",
    "soap": "صابون", "brush": "فرشاة",
    
    # إلكترونيات
    "phone": "هاتف", "iphone": "آيفون", "samsung": "سامسونج",
    "laptop": "لاب توب", "computer": "كمبيوتر", "tablet": "تابلت",
    "ipad": "آيباد", "airpods": "أيربودز", "headphones": "سماعات رأس",
    "earbuds": "سماعات أذن", "camera": "كاميرا",
    "tv": "تلفزيون", "television": "تلفزيون", "monitor": "شاشة",
    "keyboard": "كيبورد", "mouse": "ماوس", "charger": "شاحن",
    "cable": "كيبل", "power bank": "باور بنك", "battery": "بطارية",
    "smart watch": "ساعة ذكية", "speaker": "سماعة", "router": "راوتر",
    
    # منزل
    "refrigerator": "ثلاجة", "fridge": "ثلاجة", "washing machine": "غسالة",
    "vacuum cleaner": "مكنسة كهربائية", "air conditioner": "مكيف",
    "heater": "دفاية", "fan": "مروحة", "blender": "خلاط",
    "mixer": "عجانة", "oven": "فرن", "microwave": "مايكرويف",
    "toaster": "محمصة", "kettle": "غلاية", "coffee maker": "ماكينة قهوة",
    "iron": "مكواة", "hair dryer": "مجفف شعر",
    "chair": "كرسي", "table": "طاولة", "desk": "مكتب",
    "bed": "سرير", "sofa": "كنبة", "lamp": "لمبة", "mirror": "مرآة",
    "carpet": "سجادة", "curtain": "ستارة", "pillow": "مخدة",
    
    # رياضة
    "treadmill": "جهاز مشي", "dumbbell": "دمبل", "yoga mat": "حصيرة يوغا",
    "bicycle": "دراجة", "ball": "كرة", "gym": "جيم",
    
    # خامات
    "denim": "جينز", "leather": "جلد", "suede": "شمواه",
    "velvet": "مخمل", "satin": "ساتان", "silk": "حرير",
    "cotton": "قطن", "linen": "كتان", "wool": "صوف",
    "knit": "محبوك", "mesh": "شبك", "lace": "دانتيل",
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
    "checked": "مربعات", "plaid": "مربعات", "polka dot": "منقط",
    "tie dye": "تاي داي", "camouflage": "تمويه", "solid": "سادة",
    "plain": "سادة", "ombre": "تدرج لوني",
    
    # قصات وأنماط
    "slim fit": "ضيق", "regular fit": "عادي", "loose fit": "واسع",
    "oversized": "واسع", "skinny": "سكيني", "straight": "مستقيم",
    "wide leg": "رجل واسعة", "flare": "منفوش", "bootcut": "بوت كت",
    "cropped": "قصير", "crop": "قصير", "mini": "ميني", "midi": "ميدي", "maxi": "ماكسي",
    "high waist": "خصر عالي", "low waist": "خصر منخفض",
    "bodycon": "ضيق", "a-line": "قصة A", "peplum": "ببلوم",
    "wrap": "لف", "off shoulder": "اكتاف مكشوفة",
    "one shoulder": "كتف واحد", "cold shoulder": "كتف مكشوف",
    "asymmetric": "غير متناظر", "layered": "متعدد الطبقات",
    
    # تفاصيل
    "ruched": "مكشكش", "pleated": "مطوي", "frill": "كشكشة",
    "ruffle": "كشكشة", "smocked": "مطاطي", "shirred": "مطاطي",
    "embroidered": "مطرز", "beaded": "خرز", "sequined": "ترتر",
    "cut out": "قصات", "slit": "شق", "zipper": "سحاب",
    "button": "زرار", "button front": "أزرار أمامية",
    "drawstring": "رباط", "belted": "بحزام", "pocket": "جيب",
    "hooded": "بهودي", "collar": "ياقة", "lapel": "ياقة",
    "bow": "فيونكة", "strap": "حمالة", "spaghetti strap": "حمالة رفيعة",
    
    # رقاب
    "v-neck": "رقبة V", "round neck": "رقبة دائرية", "crew neck": "رقبة دائرية",
    "square neck": "رقبة مربعة", "halter": "هالتر",
    "high neck": "رقبة عالية", "mock neck": "رقبة نصف عالية",
    "turtleneck": "رقبة سلحفاة", "polo neck": "رقبة بولو",
    "scoop neck": "رقبة واسعة",
    
    # أكمام
    "long sleeve": "أكمام طويلة", "short sleeve": "أكمام قصيرة",
    "sleeveless": "بلا أكمام", "cap sleeve": "كم قصير",
    "puff sleeve": "كم منفوخ", "bell sleeve": "كم جرس",
    "bishop sleeve": "كم واسع", "raglan sleeve": "كم راجلان",
    "drop shoulder": "كتف منخفض",
    
    # أطفال
    "baby": "بيبي", "toddler": "طفل صغير", "infant": "رضيع",


SKIP_WORDS = {
    "shein", "for", "with", "and", "the", "a", "an", "in", "on", "at", "to", "of",
    "by", "from", "up", "out", "new", "hot", "sale", "best", "top", "fashion",
    "style", "look", "trend", "collection", "brand", "designer", "premium",
    "quality", "cheap", "affordable", "luxury", "exclusive", "limited",
    "edition", "season", "spring", "summer", "autumn", "fall", "winter",
    "2023", "2024", "2025", "2026", "pcs", "pc", "pack", "set", "piece",
    "pieces", "x", "xl", "xxl", "s", "m", "l", "xs", "xxxl", "one size",
    "plus size", "size", "cm", "mm", "inch", "inches", "ml", "g", "kg",
    "oz", "lb", "gb", "tb", "mb", "mah", "w", "v", "hz",
    "usd", "eur", "gbp", "sar", "aed", "qar", "kwd", "egp",
    "off", "discount", "clearance", "deal", "promo",
}

GENDER_MARKERS = {
    "women", "woman", "ladies", "lady", "female", "womens", "women's",
    "men", "man", "male", "mens", "men's", "gentleman", "gentlemen",
    "girls", "girl", "boys", "boy", "kids", "children", "child",
    "baby", "toddler", "infant", "newborn", "youth", "teen",
}


def detect_gender(title):
    title_lower = title.lower()
    has_female = any(w in title_lower for w in ["women", "woman", "ladies", "lady", "female", "womens", "women's", "girl's", "girls'", "dress", "skirt", "blouse", "lingerie", "bra", "panty", "heels", "handbag", "clutch", "maternity", "bride", "bridal"])
    has_male = any(w in title_lower for w in ["men", "man", "male", "mens", "men's", "boy's", "boys'", "suit", "blazer", "tuxedo", "bow tie", "cufflinks", "suspenders", "trousers", "chinos", "aftershave", "cologne", "beard", "mustache"])
    has_kids = any(w in title_lower for w in ["kids", "children", "child", "baby", "toddler", "infant", "newborn", "onesie", "bib", "diaper", "stroller", "crib", "pacifier"])
    
    if has_kids:
        return "kids"
    if has_female and not has_male:
        return "female"
    if has_male and not has_female:
        return "male"
    return "neutral"


def extract_keywords(title):
    clean = title.lower()
    clean = re.sub(r'[^\w\s\-]', ' ', clean)
    clean = re.sub(r'\s+', ' ', clean).strip()
    words = clean.split()
    
    found = []
    i = 0
    while i < len(words):
        if i + 1 < len(words):
            two = f"{words[i]} {words[i+1]}"
            if two in WORDS:
                found.append((two, WORDS[two]))
                i += 2
                continue
            two_dash = f"{words[i]}-{words[i+1]}"
            if two_dash in WORDS:
                found.append((two_dash, WORDS[two_dash]))
                i += 2
                continue
        
        w = words[i]
        if w in WORDS:
            found.append((w, WORDS[w]))
        elif w not in SKIP_WORDS and w not in GENDER_MARKERS:
            if not re.match(r'^\d+$', w) and len(w) > 2:
                tr = translate_word(w)
                if tr and tr != w:
                    found.append((w, tr))
        i += 1
    
    return found


def translate_word(word):
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {"client": "gtx", "sl": "en", "tl": "ar", "dt": "t", "q": word}
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        r = requests.get(url, params=params, headers=headers, timeout=5)
        if r.status_code == 200:
            data = r.json()
            if data and data[0]:
                return data[0][0][0]
    except Exception:
        pass
    return word


def build_description(keywords, gender):
    if not keywords:
        return "منتج مميز"
    
    types = []
    colors = []
    materials = []
    fits = []
    necks = []
    sleeves = []
    details = []
    patterns = []
    
    type_keywords = {"فستان", "فستان سهرة", "قميص", "بلوزة", "توب", "تيشيرت", "هودي", "سويت شيرت", "جاكيت", "معطف", "بليزر", "كارديجان", "سترة", "بولوفر", "بنطلون", "جينز", "شينو", "شورت", "تنورة", "ليقنز", "جمبسوت", "رومبر", "بدي", "أوفرول", "جوارب", "جورب شفاف", "شرابات", "حذاء", "سنيكرز", "حذاء رياضي", "بوت", "بوت كاحل", "صندل", "شبشب", "كعب عالي", "كعب", "باليرينا", "لوفر", "أوكسفورد", "شنطة", "شنطة يد", "شنطة ظهر", "توت باج", "كلتش", "كروس بودي", "محفظة", "حزام", "ربطة عنق", "وشاح", "قفازات", "قبعة", "كاب", "نظارة شمسية", "ساعة", "مجوهرات", "عقد", "سوار", "خاتم", "حلق", "عطر", "كولونيا", "ميك أب", "أحمر شفاه", "لمع شفاه", "كريم أساس", "ماسكارا", "آيلاينر", "ظل عيون", "بلاشر", "هايلايتر", "كونسيلر", "برايمر", "فيكس سبري", "كريم", "لوشن", "سيروم", "تونر", "مرطب", "واقي شمس", "شامبو", "بلسم", "ماسك", "صابون", "فرشاة", "هاتف", "آيفون", "سامسونج", "لاب توب", "كمبيوتر", "تابلت", "آيباد", "أيربودز", "سماعات رأس", "سماعات أذن", "كاميرا", "تلفزيون", "شاشة", "كيبورد", "ماوس", "شاحن", "كيبل", "باور بنك", "بطارية", "ساعة ذكية", "سماعة", "راوتر", "ثلاجة", "غسالة", "مكنسة كهربائية", "مكيف", "دفاية", "مروحة", "خلاط", "عجانة", "فرن", "مايكرويف", "محمصة", "غلاية", "ماكينة قهوة", "مكواة", "مجفف شعر", "كرسي", "طاولة", "مكتب", "سرير", "كنبة", "لمبة", "مرآة", "سجادة", "ستارة", "مخدة", "جهاز مشي", "دمبل", "حصيرة يوغا", "دراجة", "كرة", "جيم"}
    color_keywords = {"أسود", "أبيض", "أحمر", "أزرق", "أخضر", "أصفر", "وردي", "بنفسجي", "برتقالي", "بني", "بيج", "رمادي", "كحلي", "عنابي", "زيتي", "كاكي", "كريمي", "عاجي", "ذهبي", "فضي", "روز جولد", "متعدد الألوان", "سادة", "مطبوع", "زهري", "مخطط", "مربعات", "منقط", "تاي داي", "تمويه", "تدرج لوني"}
    material_keywords = {"جينز", "جلد", "شمواه", "مخمل", "ساتان", "حرير", "قطن", "كتان", "صوف", "محبوك", "شبك", "دانتيل", "شيفون", "أورجانزا", "ترتر"}
    fit_keywords = {"ضيق", "عادي", "واسع", "سكيني", "مستقيم", "رجل واسعة", "منفوش", "بوت كت", "قصير", "ميني", "ميدي", "ماكسي", "خصر عالي", "خصر منخفض", "قصة A", "ببلوم", "لف", "اكتاف مكشوفة", "كتف واحد", "كتف مكشوف", "غير متناظر", "متعدد الطبقات"}
    neck_keywords = {"رقبة V", "رقبة دائرية", "رقبة مربعة", "هالتر", "رقبة عالية", "رقبة نصف عالية", "رقبة سلحفاة", "رقبة بولو", "رقبة واسعة"}
    sleeve_keywords = {"أكمام طويلة", "أكمام قصيرة", "بلا أكمام", "كم قصير", "كم منفوخ", "كم جرس", "كم واسع", "كم راجلان", "كتف منخفض"}
    pattern_keywords = {"كاجوال", "رسمي", "حفلات", "سهرة", "فينتاج", "بوهو", "بريبي", "ستريت وير", "أنيق", "شيك", "ترندي", "مينيمال", "كلاسيك"}
    
    for eng, ar in keywords:
        if ar in type_keywords:
            types.append(ar)
        elif ar in color_keywords:
            colors.append(ar)
        elif ar in material_keywords:
            materials.append(ar)
        elif ar in fit_keywords:
            fits.append(ar)
        elif ar in neck_keywords:
            necks.append(ar)
        elif ar in sleeve_keywords:
            sleeves.append(ar)
        elif ar in pattern_keywords:
            patterns.append(ar)
        else:
            details.append(ar)
    
    parts = []
    if types:
        parts.append(types[-1])
    
    gender_word = {"female": "نسائي", "male": "رجالي", "kids": "أطفال", "neutral": ""}
    if gender in gender_word and gender_word[gender]:
        parts.append(gender_word[gender])
    
    desc_parts = []
    if colors:
        desc_parts.append(colors[0])
    if materials:
        desc_parts.append(materials[0])
    if fits:
        desc_parts.append(fits[0])
    if necks:
        desc_parts.append(necks[0])
    if sleeves:
        desc_parts.append(sleeves[0])
    if patterns:
        desc_parts.append(patterns[0])
    if details:
        desc_parts.extend(details[:2])
    
    if desc_parts:
        parts.extend(desc_parts)
    
    result = " ".join(parts)
    result = re.sub(r'\s+', ' ', result).strip()
    
    return result if result else "منتج مميز"


def summarize_product(title):
    gender = detect_gender(title)
    keywords = extract_keywords(title)
    return build_description(keywords, gender)


def is_shein_url(url):
    return "shein.com" in url.lower() or "onelink.shein.com" in url.lower()


def get_shein_product(url):
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    ]

    for attempt, ua in enumerate(user_agents):
        try:
            delay = (2 ** attempt) + random.uniform(0.5, 2.0)
            if attempt > 0:
                time.sleep(delay)

            session = requests.Session()
            headers = {
                "User-Agent": ua,
                "Accept-Language": "ar-SA,ar;q=0.9,en-US;q=0.8,en;q=0.7",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Cache-Control": "max-age=0",
                "Referer": "https://www.google.com/",
            }

            proxies = {}
            if PROXY_URL:
                proxies = {"http": PROXY_URL, "https": PROXY_URL}

            r = session.get(url, headers=headers, timeout=15, proxies=proxies, allow_redirects=True)

            if r.status_code != 200 or len(r.text) < 3000:
                continue

            soup = BeautifulSoup(r.text, "html.parser")

            title = None
            og_title = soup.select_one('meta[property="og:title"]')
            if og_title:
                title = og_title.get("content", "").strip()
            if not title:
                tw_title = soup.select_one('meta[name="twitter:title"]')
                if tw_title:
                    title = tw_title.get("content", "").strip()
            if not title:
                title_tag = soup.select_one("title")
                if title_tag:
                    title = title_tag.get_text(strip=True)
                    title = re.sub(r"\s*\|\s*SHEIN.*$", "", title, flags=re.IGNORECASE)

            image = None
            og_image = soup.select_one('meta[property="og:image"]')
            if og_image:
                image = og_image.get("content", "").strip()
            if not image:
                tw_image = soup.select_one('meta[name="twitter:image"]')
                if tw_image:
                    image = tw_image.get("content", "").strip()

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


def generate_post(product_data, original_url):
    title = product_data.get("full_title", "")
    product_name = summarize_product(title)

    # إرسال اسم القطعة والرابط فقط
    post = f"{product_name}\n\n{original_url}"
    return post


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

        post = generate_post(product, original_url)

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
                print(f"Error sending text: {e2}")
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
            print(f"Webhook processing error: {e}")
            return "Bad Request", 400
    else:
        return "Unsupported Media Type", 415

def start_webhook():
    if WEBHOOK_HOST:
        bot.remove_webhook()
        time.sleep(0.5)
        bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH)
        print(f"✅ Webhook set to: {WEBHOOK_URL_BASE}{WEBHOOK_URL_PATH}")
    else:
        print("⚠️ RENDER_EXTERNAL_HOSTNAME not set, running in local mode...")

    app.run(host="0.0.0.0", port=WEBHOOK_PORT)

if __name__ == "__main__":
    start_webhook()
