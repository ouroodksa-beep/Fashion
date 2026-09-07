import os
import re
import time
import random
import json
import requests
from bs4 import BeautifulSoup
from flask import Flask, request
import telebot

TOKEN = os.environ.get("BOT_TOKEN", "8888709197:AAEVCTpVticEzi-NBaWRdIQDmKJSxdRzA54")
bot = telebot.TeleBot(TOKEN)

PROXY_URL = os.environ.get("PROXY_URL")

# ─── قاموس: إنجليزي ← عربي (باللهجة الخليجية) ───
WORDS = {
    # أنواع الملابس
    "dress": "فستان", "frock": "فستان", "gown": "فستان سهرة",
    "shirt": "قميص", "blouse": "بلوزة", "top": "توب",
    "t-shirt": "تيشيرت", "t shirt": "تيشيرت", "tee": "تيشيرت",
    "hoodie": "هودي", "sweatshirt": "سويت شيرت",
    "jacket": "جاكيت", "coat": "كوت", "blazer": "بليزر",
    "cardigan": "كارديجان", "sweater": "بلوفر", "pullover": "بلوفر",
    "pants": "بنطلون", "trousers": "بنطلون", "jeans": "جينز",
    "chinos": "بنطلون شينو", "shorts": "شورت", "skirt": "تنورة",
    "leggings": "لقنز", "jumpsuit": "جمبسوت", "romper": "رومبر",
    "bodysuit": "بدي", "overalls": "أوفرول",
    "socks": "شرابات", "tights": "شراب شفاف", "stockings": "شرابات",
    "pajamas": "بيجامة", "pyjamas": "بيجامة", "nightwear": "قميص نوم",
    "lingerie": "لانجري", "bra": "برا", "underwear": "ملابس داخلية",
    
    # أحذية
    "shoes": "شوز", "sneakers": "سنيكرز", "trainers": "شوز رياضي",
    "boots": "بوت", "ankle boots": "هاف بوت", "sandals": "صندل",
    "slippers": "سليبر", "heels": "كعب", "pumps": "كعب",
    "flats": "فلات", "loafers": "لوفر", "oxfords": "شوز أوكسفورد",
    
    # شنط وإكسسوارات
    "bag": "شنطة", "handbag": "شنطة يد", "backpack": "شنطة ظهر",
    "tote": "شنطة توت", "clutch": "كلتش", "crossbody": "شنطة كروس",
    "wallet": "بوك", "belt": "حزام", "tie": "كرافتة",
    "scarf": "سكارف", "gloves": "دُسوس", "hat": "قبعة", "cap": "كاب",
    "sunglasses": "نظارة شمسية", "watch": "ساعة",
    "jewelry": "مجوهرات", "necklace": "سلسال", "bracelet": "أسورة",
    "ring": "خاتم", "earrings": "تراجي", "earring": "تراجي", "mirror": "منظرة",
    
    # عناية ومكياج
    "perfume": "عطر", "fragrance": "عطر", "cologne": "كولونيا",
    "makeup": "ميك أب", "lipstick": "رُوج", "lip gloss": "قلوس",
    "foundation": "فاونديشن", "mascara": "ماسكارا",
    "eyeliner": "آيلاينر", "eyeshadow": "شدو",
    "blush": "بلاشر", "highlighter": "هايلايتر", "concealer": "كونسيلر",
    "primer": "برايمر", "setting spray": "مثبت ميك أب",
    "cream": "كريم", "lotion": "لوشن", "serum": "سيروم",
    "toner": "تونر", "moisturizer": "مرطب", "sunscreen": "واقي شمس",
    "shampoo": "شامبو", "conditioner": "بلسم", "mask": "ماسك",
    "soap": "صابون", "brush": "فرشاة",
    
    # خامات
    "denim": "جينز", "leather": "جلد", "suede": "شمواه",
    "velvet": "مخمل", "satin": "ساتان", "silk": "حرير",
    "cotton": "قطن", "linen": "كتان", "wool": "صوف",
    "knit": "محبوك", "knitted": "تريكو", "mesh": "تور", "lace": "دانتيل",
    "chiffon": "شيفون", "organza": "أورجانزا", "sequin": "ترتر",
    
    # ألوان
    "black": "أسود", "white": "أبيض", "red": "أحمر", "blue": "أزرق",
    "green": "أخضر", "yellow": "أصفر", "pink": "وردي", "purple": "بنفسجي",
    "orange": "برتقالي", "brown": "بني", "beige": "بيج", "grey": "رمادي",
    "gray": "رمادي", "navy": "كحلي", "burgundy": "عنابي", "maroon": "عنابي",
    "olive": "زيتي", "khaki": "كاكي", "cream": "أوف وايت", "ivory": "سكري",
    "gold": "ذهبي", "silver": "فضي", "rose gold": "روز جولد",
    "multicolor": "مشكل ألوان", "colorful": "ملون",
    "printed": "مشجر", "floral": "ورد", "striped": "مقلم",
    "checked": "كاروهات", "plaid": "مربعات", "polka dot": "منقط",
    "solid": "سادة", "plain": "سادة",
    
    # قصات وأنماط
    "slim fit": "سمارت فت", "regular fit": "قصة العادية", "loose fit": "وايد/واسع",
    "oversized": "أوفر سايز", "skinny": "سكيني", "straight": "قصة سيدة",
    "wide leg": "رجل واسعة", "flare": "كلوش", "cropped": "قصير", 
    "crop": "كروب", "mini": "قصيرة", "midi": "ميدي", "maxi": "طويل",
    "high waist": "هاي ويست", "low waist": "خصر واطي",
    "loose": "راهي/واسع",
    
    # تفاصيل
    "ruched": "زمّ/كشكشة", "pleated": "بليسيه", "ruffle": "كشكشة",
    "embroidered": "مطرز", "zipper": "سحاب", "button": "أزرار",
    "v-neck": "فتحة V", "v neck": "فتحة V", "round neck": "رقبة دائرية",
    "polo neck": "ياقة بولو", "polo": "بولو",
    "long sleeve": "كم طويل", "short sleeve": "كم قصير",
    "sleeveless": "كت/بدون أكمام", "puff sleeve": "أكمام منفوخة",
    "boho": "بوهيمي", "casual": "كاجوال",
    
    # عدد القطع
    "set": "طقم", "pack": "مجموعة", "bundle": "طقم",
}

TYPE_SET = {"فستان", "فستان سهرة", "قميص", "بلوزة", "توب", "تيشيرت", "هودي",
            "سويت شيرت", "جاكيت", "كوت", "بليزر", "كارديجان", "بلوفر",
            "بنطلون", "جينز", "بنطلون شينو", "شورت", "تنورة", "لقنز", "جمبسوت", "رومبر",
            "بدي", "أوفرول", "بيجامة", "قميص نوم", "لانجري", "برا", "ملابس داخلية",
            "شوز", "سنيكرز", "صندل", "كعب", "فلات",
            "لوفر", "شوز أوكسفورد", "بوت", "هاف بوت", "سليبر", "شوز رياضي",
            "شنطة", "شنطة يد", "شنطة ظهر", "شنطة توت", "كلتش", "شنطة كروس",
            "بوك", "حزام", "كرافتة", "سكارف", "دُسوس", "قبعة", "كاب",
            "نظارة شمسية", "ساعة", "مجوهرات", "سلسال", "أسورة", "خاتم", "تراجي", "منظرة",
            "عطر", "كولونيا", "ميك أب", "رُوج", "قلوس", "فاونديشن",
            "ماسكارا", "آيلاينر", "شدو", "بلاشر", "هايلايتر", "كونسيلر",
            "برايمر", "مثبت ميك أب", "كريم", "لوشن", "سيروم", "تونر", "مرطب",
            "واقي شمس", "شامبو", "بلسم", "ماسك", "صابون", "فرشاة",
            "شرابات", "شراب شفاف"}

COLOR_SET = {"أسود", "أبيض", "أحمر", "أزرق", "أخضر", "أصفر", "وردي", "بنفسجي",
             "برتقالي", "بني", "بيج", "رمادي", "كحلي", "عنابي", "زيتي", "كاكي",
             "أوف وايت", "سكري", "ذهبي", "فضي", "روز جولد", "مشكل ألوان", "سادة",
             "مشجر", "ورد", "مقلم", "كاروهات", "منقط"}

MATERIAL_SET = {"جينز", "جلد", "شمواه", "مخمل", "ساتان", "حرير", "قطن", "كتان",
                "صوف", "محبوك", "تريكو", "تور", "دانتيل", "شيفون", "أورجانزا", "ترتر"}

FIT_SET = {"سمارت فت", "القصة العادية", "وايد/واسع", "أوفر سايز", "سكيني", "قصة سيدة", "رجل واسعة", "كلوش", "قصيرة",
           "ميدي", "طويل", "هاي ويست", "خصر واطي"}

NECK_SET = {"فتحة V", "رقبة دائرية", "ياقة بولو", "بولو"}
SLEEVE_SET = {"كم طويل", "كم قصير", "كت/بدون أكمام", "أكمام منفوخة"}
DETAIL_SET = {"زمّ/كشكشة", "بليسيه", "كشكشة", "مطرز", "سحاب", "أزرار", "بوهيمي", "كاجوال"}

EMOJI_MAP = {
    "فستان": "👗", "فستان سهرة": "✨", "قميص": "👔", "بلوزة": "👚", "توب": "👕",
    "تيشيرت": "👕", "هودي": "🧥", "سويت شيرت": "🧥", "جاكيت": "🧥", "كوت": "🧥",
    "بليزر": "🤵", "كارديجان": "🧶", "بلوفر": "🧶",
    "بنطلون": "👖", "جينز": "👖", "شورت": "🩳", "تنورة": "👗",
    "لقنز": "🖤", "جمبسوت": "👗", "رومبر": "👗", "بدي": "👙", "أوفرول": "👖",
    "بيجامة": "🌙", "قميص نوم": "🌙", "لانجري": "💋", "برا": "👙", "ملابس داخلية": "👙",
    "شوز": "👞", "سنيكرز": "👟", "صندل": "🩴", "كعب": "👠",
    "فلات": "🥿", "لوفر": "👞", "بوت": "👢", "هاف بوت": "👢",
    "سليبر": "🩴", "شوز رياضي": "👟",
    "شنطة": "👜", "شنطة يد": "👜", "شنطة ظهر": "🎒", "شنطة توت": "🛍️", "كلتش": "👝",
    "شنطة كروس": "👜", "بوك": "👛", "حزام": "🖤", "سكارف": "🧣",
    "قبعة": "🎩", "كاب": "🧢", "نظارة شمسية": "🕶️", "ساعة": "⌚",
    "مجوهرات": "💎", "سلسال": "📿", "أسورة": "📿", "خاتم": "💍", "تراجي": "💎", "منظرة": "🪞",
    "عطر": "🌸", "كولونيا": "🌸", "ميك أب": "💄", "رُوج": "💋", "قلوس": "💋",
    "فاونديشن": "💄", "ماسكارا": "👁️", "آيلاينر": "👁️", "شدو": "👁️",
    "بلاشر": "🌸", "هايلايتر": "✨", "كونسيلر": "💄", "برايمر": "💄",
    "مثبت ميك أب": "💨", "كريم": "🧴", "لوشن": "🧴", "سيروم": "🧴", "تونر": "🧴",
    "مرطب": "🧴", "واقي شمس": "☀️", "شامبو": "🧴", "بلسم": "🧴", "ماسك": "🧖‍♀️",
    "صابون": "🧼", "فرشاة": "🖌️",
}

# ─── قوالب تسويقية دنياميكية لضمان عدم التكرار ───
HOOKS = [
    "🔥 صيدة اليوم الجبّارة!",
    "✨ قطعتك الجديدة لطلّة كشخة!",
    "🛍️ شوفوا هالقطعة الذوق وشلون تجنن!",
    "💫 خيارك المثالي لإطلالة متميزة!",
    "😍 إناقة وتفاصيل تفتح النفس!",
    "🌟 صيدة أنيقة لا تفوتكم!",
]

PUNCHLINES = [
    "شوفي التفاصيل واطلبيه قبل يخلص! 💥",
    "يستاهل يكون بكسوة دولابك ✨",
    "كمية أناقة مو طبيعية لا تطوفك 🔥",
    "اطلبيه الحين وتأنّقي على أصول! 🛍️",
    "ترند الفتره وطلب عليه عالي ⚡",
]

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
            if n == 1:
                return None
            elif n == 2:
                return "طقم قطعتين"
            elif n == 3:
                return "طقم 3 قطع"
            else:
                return f"طقم {n} قطع"
    if re.search(r'\b(?:set|pack|bundle)\b', t):
        return "طقم كامل"
    return None

def detect_gender(title, main_type=""):
    t = title.lower()
    female = ["women", "woman", "ladies", "lady", "female", "womens", "women's",
              "girl's", "girls'", "dress", "skirt", "blouse", "heels", "handbag",
              "blush", "lipstick", "gown", "frock", "tights", "leggings", "bodysuit",
              "romper", "jumpsuit", "cardigan", "clutch", "tote", "crossbody",
              "earrings", "necklace", "bracelet", "maxi", "midi", "mini", "bra",
              "pajamas", "pyjamas", "nightwear", "lingerie"]
    male = ["men", "man", "male", "mens", "men's", "boy's", "boys'",
            "suit", "tuxedo", "chinos", "oxfords", "loafers", "tie", "belt", "blazer"]
    kids = ["kids", "children", "child", "baby", "toddler", "infant", "newborn"]
    
    def has_word(text, lst):
        for w in lst:
            if re.search(r'\b' + re.escape(w) + r'\b', text):
                return True
        return False
    
    has_f = has_word(t, female)
    has_m = has_word(t, male)
    has_k = has_word(t, kids)
    
    if has_k:
        if has_f and not has_m:
            return "بناتي 👧"
        if has_m and not has_f:
            return "ولادي 👦"
        return "أطفالي 🧒"
    
    female_only = {"فستان", "فستان سهرة", "بلوزة", "تنورة", "كعب",
                   "فلات", "شنطة يد", "كلتش", "شنطة توت", "شنطة كروس", "بلاشر",
                   "رُوج", "قلوس", "ماسكارا", "آيلاينر", "شدو", "هايلايتر",
                   "كونسيلر", "برايمر", "مثبت ميك أب", "رومبر", "بدي", "جمبسوت",
                   "بيجامة", "قميص نوم", "لانجري", "برا", "ملابس داخلية"}
    male_only = {"كرافتة", "بليزر", "شوز أوكسفورد", "لوفر"}
    
    if main_type in female_only:
        return "نسائي 👩"
    if main_type in male_only:
        return "رجالي 👨"
    
    if has_f and not has_m:
        return "نسائي 👩"
    if has_m and not has_f:
        return "رجالي 👨"
    return ""

def extract_smart_data(title):
    clean = title.lower()
    clean = re.sub(r'com\.\w+', '', clean)
    clean = re.sub(r'[^\w\s\-]', ' ', clean)
    words = clean.split()
    
    found_types = []
    i = 0
    while i < len(words):
        if i < len(words) - 1:
            two = f"{words[i]} {words[i+1]}"
            if two in WORDS and WORDS[two] in TYPE_SET:
                tr = WORDS[two]
                if tr not in found_types:
                    found_types.append(tr)
                i += 2
                continue
        if words[i] in WORDS and WORDS[words[i]] in TYPE_SET:
            tr = WORDS[words[i]]
            if tr not in found_types:
                found_types.append(tr)
            i += 1
            continue
        i += 1

    if not found_types:
        main_type_str = "قطعة"
        first_type = "قطعة"
    elif len(found_types) == 1:
        main_type_str = found_types[0]
        first_type = found_types[0]
    else:
        main_type_str = " و ".join(found_types)
        first_type = found_types[0]

    accessory_words = {"chain", "strap", "line", "button", "buckle", "print", "pattern", "trim", "border"}
    extracted_color = ""
    
    for idx, w in enumerate(words):
        translated = WORDS.get(w)
        if translated in COLOR_SET and translated != "سادة":
            next_word = words[idx+1] if idx + 1 < len(words) else ""
            if next_word not in accessory_words:
                extracted_color = translated
                break

    materials, fits, necks, sleeves, details = [], [], [], [], []
    for w in words:
        tr = WORDS.get(w)
        if tr in MATERIAL_SET and tr not in materials: materials.append(tr)
        if tr in FIT_SET and tr not in fits: fits.append(tr)
        if tr in NECK_SET and tr not in necks: necks.append(tr)
        if tr in SLEEVE_SET and tr not in sleeves: sleeves.append(tr)
        if tr in DETAIL_SET and tr not in details: details.append(tr)

    return {
        "main_type_str": main_type_str,
        "first_type": first_type,
        "color": extracted_color,
        "material": materials[0] if materials else "",
        "fit": fits[0] if fits else "",
        "neck": necks[0] if necks else "",
        "sleeve": sleeves[0] if sleeves else "",
        "detail": details[0] if details else ""
    }

# ─── بناء الوصف التسويقي المتغير والديناميكي ───
def build_description(title):
    data = extract_smart_data(title)
    
    main_type_str = data["main_type_str"]
    first_type = data["first_type"]
    color = data["color"]
    material = data["material"]
    fit = data["fit"]
    neck = data["neck"]
    sleeve = data["sleeve"]
    detail = data["detail"]
    
    quantity = extract_quantity(title)
    gender = detect_gender(title, first_type)
    emoji = EMOJI_MAP.get(first_type, "✨")
    
    # بناء تفاصيل المنتج الأساسية
    item_parts = []
    if quantity:
        item_parts.append(f"{quantity}")
    
    core = main_type_str
    if material:
        core += f" من {material}"
    if color:
        core += f" بلون {color}"
        
    item_parts.append(core)
    if gender:
        item_parts.append(f"({gender})")
        
    product_line = " ".join(item_parts)
    
    # تجميع الميزات الإضافية
    extras = []
    if fit: extras.append(f"قصة {fit}")
    if neck: extras.append(neck)
    if sleeve: extras.append(sleeve)
    if detail: extras.append(f"تفاصيل {detail}")
    
    # اختيار عناصر تسويقية عشوائية لكل بوست لضمان التنوع
    hook = random.choice(HOOKS)
    punchline = random.choice(PUNCHLINES)
    
    # دمج المكونات في بوست تسويقي متكامل
    post_lines = [f"{hook}\n"]
    post_lines.append(f"📌 {product_line} {emoji}")
    
    if extras:
        extra_str = " • ".join(extras)
        post_lines.append(f"✨ المميزات: {extra_str}")
        
    post_lines.append(f"\n💡 {punchline}")
    
    return re.sub(r' +', ' ', "\n".join(post_lines)).strip()

def is_shein_url(url):
    return any(domain in url.lower() for domain in ["shein.com", "shein.top", "onelink.shein.com"])

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

        wait = bot.reply_to(msg, "⏳ جاري استخراج البيانات...")

        product = get_shein_product(original_url)

        if not product:
            bot.edit_message_text("❌ تعذر قراءة بيانات المنتج، حاول مرة ثانية", msg.chat.id, wait.message_id)
            continue

        product_name = build_description(product["full_title"])
        post = f"{product_name}\n\n🛒 رابط الطلب أونلاين:\n{original_url}"

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

def start_webhook():
    if WEBHOOK_HOST:
        bot.remove_webhook()
        time.sleep(0.5)
        bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH)

    app.run(host="0.0.0.0", port=WEBHOOK_PORT)

if __name__ == "__main__":
    start_webhook()
