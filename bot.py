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
    "black": "الأسود", "white": "الأبيض", "red": "الأحمر", "blue": "الأزرق",
    "green": "الأخضر", "yellow": "الأصفر", "pink": "الوردي", "purple": "البنفسجي",
    "orange": "البرتقالي", "brown": "البني", "beige": " البيج", "grey": "الرمادي",
    "gray": "الرمادي", "navy": "الكحلي", "burgundy": "العنابي", "maroon": "العنابي",
    "olive": "الزيتي", "khaki": "الكاكي", "cream": "الكريمي", "ivory": "العاجي",
    "gold": "الذهبي", "silver": "الفضي", "rose gold": "الروز جولد",
    "multicolor": "متعدد الألوان", "colorful": "الملون",
    "printed": "المطبوع", "floral": "الزهري", "striped": "المخطط",
    "checked": "الكاروهات", "plaid": "الكاروهات", "polka dot": "المنقط",
    "solid": "سادة", "plain": "سادة",
    
    # قصات وأنماط
    "slim fit": "ضيق", "regular fit": "عادي", "loose fit": "واسع",
    "oversized": "أوفر سايز واسع", "skinny": "سكيني", "straight": "مستقيم",
    "wide leg": "برجل واسعة", "flare": "منفوش", "cropped": "قصير", 
    "crop": "قصير", "mini": "ميني", "midi": "ميدي", "maxi": "ماكسي",
    "high waist": "بخصر عالي", "low waist": "بخصر منخفض",
    "loose": "واسع",
    
    # تفاصيل
    "ruched": "مكشكش", "pleated": "مطوي", "ruffle": "كشكشة",
    "embroidered": "مطرز", "zipper": "سحاب", "button": "أزرار",
    "v-neck": "رقبة V", "v neck": "رقبة V", "round neck": "رقبة دائرية",
    "polo neck": "رقبة بولو", "polo": "بولو",
    "long sleeve": "أكمام طويلة", "short sleeve": "أكمام قصيرة",
    "sleeveless": "بدون أكمام", "puff sleeve": "أكمام منفوخة",
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

COLOR_SET = {"الأسود", "الأبيض", "الأحمر", "الأزرق", "الأخضر", "الأصفر", "الوردي", "البنفسجي",
             "البرتقالي", "البني", " البيج", "الرمادي", "الكحلي", "العنابي", "الزيتي", "الكاكي",
             "الكريمي", "العاجي", "الذهبي", "الفضي", "الروز جولد", "متعدد الألوان", "الملون",
             "المطبوع", "الزهري", "المخطط", "الكاروهات", "المنقط"}

MATERIAL_SET = {"جينز", "جلد", "شمواه", "مخمل", "ساتان", "حرير", "قطن", "كتان",
                "صوف", "محبوك", "شبك", "دانتيل", "شيفون", "أورجانزا", "ترتر"}

FIT_SET = {"ضيق", "عادي", "واسع", "سكيني", "مستقيم", "برجل واسعة", "منفوش", "قصير",
           "ميني", "ميدي", "ماكسي", "بخصر عالي", "بخصر منخفض", "أوفر سايز واسع"}

NECK_SET = {"رقبة V", "رقبة دائرية", "رقبة بولو", "بولو"}
SLEEVE_SET = {"أكمام طويلة", "أكمام قصيرة", "بدون أكمام", "أكمام منفوخة"}
DETAIL_SET = {"مكشكش", "مطوي", "كشكشة", "مطرز", "سحاب", "أزرار", "بوهيمي", "كاجوال"}

EMOJI_MAP = {
    "فستان": "👗", "فستان سهرة": "✨", "قميص": "👔", "بلوزة": "👚", "توب": "👕",
    "تيشيرت": "👕", "هودي": "🧥", "سويت شيرت": "🧥", "جاكيت": "🧥", "معطف": "🧥",
    "بليزر": "🤵", "كارديجان": "🧶", "سترة": "🧶", "بلوفر": "🧶",
    "بنطلون": "👖", "جينز": "👖", "شينو": "👖", "شورت": "🩳", "تنورة": "👗",
    "ليقنز": "🖤", "جمبسوت": "👗", "رومبر": "👗", "بدي": "👙", "أوفرول": "👖",
    "بيجاما": "🌙", "لبس نوم": "🌙", "لانجري": "💋", "صدرية": "👙", "ملابس داخلية": "👙",
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
                return "من قطعتين"
            else:
                return f"من {n} قطع"
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
            return "بناتي"
        if has_m and not has_f:
            return "ولادي"
        return "أطفال"
    
    female_only = {"فستان", "فستان سهرة", "بلوزة", "تنورة", "كعب عالي", "كعب",
                   "باليرينا", "شنطة يد", "كلتش", "توت باج", "كروس بودي", "بلاشر",
                   "أحمر شفاه", "ملمع شفاه", "ماسكارا", "آيلاينر", "ظل عيون", "هايلايتر",
                   "كونسيلر", "برايمر", "مثبت مكياج", "رومبر", "بدي", "جمبسوت",
                   "بيجاما", "لبس نوم", "لانجري", "صدرية", "ملابس داخلية"}
    male_only = {"ربطة عنق", "بليزر", "أوكسفورد", "لوفر"}
    
    if main_type in female_only:
        return "نسائي"
    if main_type in male_only:
        return "رجالي"
    
    if has_f and not has_m:
        return "نسائي"
    if has_m and not has_f:
        return "رجالي"
    return "نسائي"  # الافتراضي لشي إن غالباً نسائي


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
    """بناء وصف جذاب وتسويقي حماسي مع القوالب المتنوعة"""
    kw = extract_keywords(title)
    
    types = [k for k in kw if k in TYPE_SET]
    colors = [k for k in kw if k in COLOR_SET]
    materials = [k for k in kw if k in MATERIAL_SET]
    fits = [k for k in kw if k in FIT_SET]
    necks = [k for k in kw if k in NECK_SET]
    sleeves = [k for k in kw if k in SLEEVE_SET]
    details = [k for k in kw if k in DETAIL_SET]
    
    main_type = max(types, key=len) if types else "القطعة"
    quantity = extract_quantity(title)
    gender = detect_gender(title, main_type)
    
    color = colors[0] if colors else ""
    material = materials[0] if materials else ""
    fit = fits[0] if fits else ""
    sleeve = sleeves[0] if sleeves else ""
    detail = details[0] if details else ""
    emoji = EMOJI_MAP.get(main_type, "✨")
    
    # تفاصيل إضافية مجمعة
    extra_details = []
    if quantity: extra_details.append(quantity)
    if fit: extra_details.append(fit)
    if material: extra_details.append(f"من خامة ال{material}")
    if sleeve: extra_details.append(sleeve)
    if detail: extra_details.append(detail)
    
    detail_str = " ".join(extra_details)
    
    # ─── صياغة العبارة حسب الفئة والجنس ───
    if gender in ["بناتي", "ولادي", "أطفال"]:
        templates = [
            f"يا عيني شوفوا كوتة هذا الـ {main_type} للأطفال {emoji}! القماشة والشكل يجنن ومرة كيوت 💕",
            f"شوفوا جمال {main_type} الأطفال هذا {emoji}! يجنن باللبس والأناقة لا توصف 👶✨",
            f"يا ناس على الجمال! شوفوا {main_type} الأطفال كيف يجنن والديزاين خطير 🔥😍",
        ]
    elif gender == "رجالي":
        templates = [
            f"شوفوا هذا الـ {main_type} الرجالي الرهيب {emoji}! خامة وقصة تفتح النفس ولا غلطة 🔥",
            f"للشباب.. شوفوا {main_type} هذا كيف فخم ومرتب! النقشة والقشة بطلة 👌✨",
            f"حق الشياكة! شوفوا هذا الـ {main_type} الرجالي الخرافة.. شياكة وأناقة لا تفوتكم 😎🔥",
        ]
    else:  # نسائي
        female_intros = [
            f"يا بنات الحقوا على هذا الـ {main_type} اللي يجنن {emoji}! شوفوا اللون {color if color else 'والتفاصيل'} كيف طالع مش ممكن 😍✨",
            f"بنات شوفوا الأناقة! {main_type} شيك ومرتب بشكل مو عادي {emoji} لازم يكون بعربتكم 🔥💖",
            f"شوفوا الروعة يا بنات! {main_type} خيالي والتفاصيل تجنن، طلته تاخد العقل 😭كيووت 💕",
            f"يا بنات شوفوا هذا الـ {main_type} العسل {emoji}! التفاصيل والقشّة تجنن والسعر بطل 🔥✨"
        ]
        templates = female_intros

    selected_intro = random.choice(templates)
    
    # إضافات إغراء للتسوق بدون ذكر سعر
    closings = [
        "شوفوا الخصم والشكل الرهيب، الحقوا عليه قبل ينفد! 🛒🔥",
        "القطعة بطلة وبتاخد العقل، لا تفوتكم بالطلب! 🛍️✨",
        "السعر والجمال خيالي، اطلبوه الحين وانتوا مغمضين! 😍👏",
        "شوفوا العرض الجبار عليه، يجنن لا يفوتكم! 💖🛒"
    ]
    selected_closing = random.choice(closings)
    
    # التجميع النهائي
    final_text = f"{selected_intro}\n"
    if detail_str:
        final_text += f"📌 التفاصيل: {detail_str}\n"
    final_text += f"\n{selected_closing}"
    
    return re.sub(r' +', ' ', final_text).strip()


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

        wait = bot.reply_to(msg, "⏳ جاري استخراج الصورة والوصف...")

        product = get_shein_product(original_url)

        if not product:
            bot.edit_message_text("❌ تعذر قراءة بيانات المنتج", msg.chat.id, wait.message_id)
            continue

        product_caption = build_description(product["full_title"])
        post = f"{product_caption}\n\n🔗 رابط المنتج:\n{original_url}"

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
