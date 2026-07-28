import telebot
import re
import time
import random
import os
import requests
from bs4 import BeautifulSoup

TOKEN = os.environ.get("BOT_TOKEN", "8888709197:AAEVCTpVticEzi-NBaWRdIQDmKJSxdRzA54")
bot = telebot.TeleBot(TOKEN)

PROXY_URL = os.environ.get("PROXY_URL")
_last_used_templates = {}

# ─── أنواع المنتجات ───
PRODUCT_TYPES = {
    "dress": "فستان", "gown": "فستان", "frock": "فستان",
    "shirt": "قميص", "blouse": "بلوزة", "top": "توب",
    "t-shirt": "تيشيرت", "t shirt": "تيشيرت", "tee": "تيشيرت",
    "hoodie": "هودي", "sweatshirt": "سويت شيرت",
    "jacket": "جاكيت", "coat": "معطف", "blazer": "بليزر",
    "cardigan": "كارديجان", "sweater": "سترة", "pullover": "بولوفر",
    "pants": "بنطلون", "trousers": "بنطلون", "jeans": "جينز",
    "shorts": "شورت", "skirt": "تنورة",
    "leggings": "ليقنز", "jumpsuit": "جمبسوت", "romper": "رومبر",
    "bodysuit": "بدي", "overalls": "أوفرول",
    "socks": "جوارب", "tights": "شرابات", "stockings": "شرابات",
    "shoes": "حذاء", "sneakers": "حذاء رياضي", "trainers": "حذاء رياضي",
    "boots": "بوت", "ankle boots": "بوت", "sandals": "صندل",
    "slippers": "شبشب", "heels": "كعب", "pumps": "كعب",
    "flats": "باليرينا", "loafers": "لوفر",
    "bag": "شنطة", "handbag": "شنطة يد", "backpack": "شنطة ظهر",
    "tote": "شنطة", "clutch": "كلتش", "crossbody": "شنطة",
    "wallet": "محفظة", "belt": "حزام", "tie": "ربطة عنق",
    "scarf": "وشاح", "gloves": "قفازات", "hat": "قبعة", "cap": "كاب",
    "sunglasses": "نظارة شمسية", "watch": "ساعة",
    "jewelry": "مجوهرات", "necklace": "عقد", "bracelet": "سوار",
    "ring": "خاتم", "earrings": "حلق", "earring": "حلق",
    "perfume": "عطر", "fragrance": "عطر", "cologne": "عطر",
    "makeup": "ميك أب", "lipstick": "أحمر شفاه", "lip gloss": "لمع شفاه",
    "foundation": "كريم أساس", "mascara": "ماسكارا",
    "eyeliner": "آيلاينر", "eyeshadow": "ظل عيون",
    "blush": "بلاشر", "highlighter": "هايلايتر", "concealer": "كونسيلر",
    "cream": "كريم", "lotion": "لوشن", "serum": "سيروم",
    "toner": "تونر", "moisturizer": "مرطب", "sunscreen": "واقي شمس",
    "shampoo": "شامبو", "conditioner": "بلسم", "mask": "ماسك",
    "soap": "صابون", "brush": "فرشاة",
    "phone": "هاتف", "iphone": "آيفون", "samsung": "هاتف",
    "laptop": "لاب توب", "computer": "كمبيوتر", "tablet": "تابلت",
    "ipad": "آيباد", "airpods": "أيربودز", "headphones": "سماعات",
    "earbuds": "سماعات", "camera": "كاميرا",
    "tv": "تلفزيون", "television": "تلفزيون", "monitor": "شاشة",
    "keyboard": "كيبورد", "mouse": "ماوس", "charger": "شاحن",
    "cable": "كيبل", "power bank": "باور بنك", "battery": "بطارية",
    "smart watch": "ساعة ذكية", "speaker": "سماعة", "router": "راوتر",
    "refrigerator": "ثلاجة", "fridge": "ثلاجة",
    "washing machine": "غسالة", "vacuum cleaner": "مكنسة",
    "air conditioner": "مكيف", "heater": "دفاية", "fan": "مروحة",
    "blender": "خلاط", "mixer": "عجانة", "oven": "فرن",
    "microwave": "مايكرويف", "toaster": "محمصة", "kettle": "غلاية",
    "coffee maker": "ماكينة قهوة", "iron": "مكواة", "hair dryer": "مجفف شعر",
    "chair": "كرسي", "table": "طاولة", "desk": "مكتب",
    "bed": "سرير", "sofa": "كنبة", "lamp": "لمبة", "mirror": "مرآة",
    "carpet": "سجادة", "curtain": "ستارة", "pillow": "مخدة",
    "treadmill": "جهاز مشي", "dumbbell": "دمبل", "yoga mat": "حصيرة يوغا",
    "bicycle": "دراجة", "ball": "كرة",
}

# ─── الألوان ───
COLORS = {
    "black": "أسود", "white": "أبيض", "red": "أحمر", "blue": "أزرق",
    "green": "أخضر", "yellow": "أصفر", "pink": "وردي", "purple": "بنفسجي",
    "orange": "برتقالي", "brown": "بني", "beige": "بيج", "grey": "رمادي",
    "gray": "رمادي", "navy": "كحلي", "burgundy": "عنابي", "maroon": "عنابي",
    "olive": "زيتي", "khaki": "كاكي", "cream": "كريمي", "ivory": "عاجي",
    "gold": "ذهبي", "silver": "فضي", "rose gold": "روز جولد",
    "multicolor": "متعدد الألوان", "colorful": "متعدد الألوان",
    "printed": "مطبوع", "floral": "زهري", "striped": "مخطط",
    "plaid": "مربعات", "checked": "مربعات", "polka dot": "منقط",
    "tie dye": "تاي داي", "camouflage": "تمويه", "ombre": "تدرج لوني",
    "solid": "سادة", "plain": "سادة",
}

# ─── تصنيف الجنس (للقوالب بس) ───
FEMALE_SIGNS = {"women", "woman", "ladies", "lady", "
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
    
    # أنماط
    "casual": "كاجوال", "formal": "رسمي", "party": "حفلات",
    "evening": "سهرة", "vintage": "فينتاج", "bohemian": "بوهو",
    "preppy": "بريبي", "streetwear": "ستريت وير",
    "elegant": "أنيق", "chic": "شيك", "trendy": "ترندي",
    "minimalist": "مينيمال", "classic": "كلاسيك",
    
    # أحذية تفاصيل
    "platform": "بلاتفورم", "wedge": "ويدج", "stiletto": "ستيليتو",
    "block heel": "كعب سميك", "knee high": "للركبة",
    "thigh high": "فوق الركبة", "ankle strap": "حمالة كاحل",
    
    # إلكترونيات تفاصيل
    "wireless": "لاسلكي", "bluetooth": "بلوتوث",
    "noise cancelling": "عزل ضوضاء", "fast charging": "شحن سريع",
    "waterproof": "مقاوم للماء",
    
    # أطفال
    "baby": "بيبي", "toddler": "طفل صغير", "infant": "رضيع",
}

# كلمات نستبعدها خالص
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
    "women", "woman", "ladies", "lady", "female", "men", "man", "male",
    "girls", "girl", "boys", "boy", "kids", "children", "child", "unisex",
    "y2k", "90s", "80s", "70s", "retro",
}

# كلمات بتدل على الجنس (للتصنيف بس، مش للوصف)
GENDER_MARKERS = {
    "women", "woman", "ladies", "lady", "female", "womens", "women's",
    "men", "man", "male", "mens", "men's", "gentleman", "gentlemen",
    "girls", "girl", "boys", "boy", "kids", "children", "child",
    "baby", "toddler", "infant", "newborn", "youth", "teen",
}


def detect_product_category(title):
    title_lower = title.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in title_lower:
                return category
    return "general"


def detect_gender(title):
    title_lower = title.lower()
    has_female = any(w in title_lower for w in ["women", "woman", "ladies", "lady", "female", "womens", "women's", "girl's", "girls'", "dress", "skirt", "blouse", "lingerie", "bra", "panty", "heels", "handbag", "clutch", "maternity", "bride", "bridal"])
    has_male = any(w in title_lower for w in ["men", "man", "male", "mens", "men's", "boy's", "boys'", "suit", "blazer", "tuxedo", "bow tie", "cufflinks", "suspenders", "trousers", "chinos", "aftershave", "cologne", "beard", "mustache"])
    has_kids = any(w in title_lower for w in ["kids", "children", "child", "baby", "toddler", "infant", "newborn", "onesie", "bib", "diaper", "stroller", "crib", "pacifier"])
    
    # أولوية الأطفال لو فيه كلمات أطفال واضحة
    if has_kids and (has_female or has_male or "girls" in title_lower or "boys" in title_lower):
        return "kids"
    if has_kids:
        return "kids"
    if has_female and not has_male:
        return "female"
    if has_male and not has_female:
        return "male"
    if has_female and has_male:
        return "neutral"  # unisex
    return "neutral"


def extract_keywords(title):
    """
    تستخرج الكلمات المهمة من العنوان وترتبهم:
    [نوع المنتج, خامة/قصة, لون, تفاصيل]
    """
    # نظف
    clean = title.lower()
    clean = re.sub(r'[^\w\s\-]', ' ', clean)  # شيل علامات الترقيم
    clean = re.sub(r'\s+', ' ', clean).strip()
    words = clean.split()
    
    found = []
    i = 0
    while i < len(words):
        # جرب كلمتين مع بعض أول (مثلاً slim fit, long sleeve)
        if i + 1 < len(words):
            two = f"{words[i]} {words[i+1]}"
            if two in WORDS:
                found.append((two, WORDS[two]))
                i += 2
                continue
            # كلمات مركبة بشرطة
            two_dash = f"{words[i]}-{words[i+1]}"
            if two_dash in WORDS:
                found.append((two_dash, WORDS[two_dash]))
                i += 2
                continue
        
        # جرب كلمة واحدة
        w = words[i]
        if w in WORDS:
            found.append((w, WORDS[w]))
        elif w not in SKIP_WORDS and w not in GENDER_MARKERS:
            # كلمة مش معروفة — نترجمها لو كانت مش رقم
            if not re.match(r'^\d+$', w) and len(w) > 2:
                # نترجمها بس نحطها في النهاية (أقل أهمية)
                tr = translate_word(w)
                if tr and tr != w:
                    found.append((w, tr))
        i += 1
    
    return found


def translate_word(word):
    """ترجمة كلمة واحدة"""
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {"client": "gtx", "sl": "en", "tl": "ar", "dt": "t", "q": word}
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        r = requests.get(url, params=params, headers=headers, timeout=5)
        if r.status_code == 200:
            data = r.json()
            if data and data[0]:
                return data[0][0][0]
    except:
        pass
    return word


def build_description(keywords, gender):
    """
    تبني وصف من الكلمات المستخرجة بترتيب منطقي:
    نوع المنتج + (جنس) + لون/خامة + تفاصيل
    """
    if not keywords:
        return "منتج مميز"
    
    # نفصل الكلمات حسب نوعها
    types = []      # نوع المنتج (فستان، قميص...)
    colors = []     # ألوان
    materials = []  # خامات
    fits = []       # قصات
    necks = []      # رقاب
    sleeves = []    # أكمام
    details = []    # تفاصيل عامة
    patterns = []   # أنماط (كاجوال، رسمي...)
    others = []     # الباقي
    
    type_keywords = {"فستان", "فستان سهرة", "قميص", "بلوزة", "توب", "تيشيرت", "هودي", "سويت شيرت", "جاكيت", "معطف", "بليزر", "كارديجان", "سترة", "بولوفر", "بنطلون", "جينز", "شينو", "شورت", "تنورة", "ليقنز", "جمبسوت", "رومبر", "بدي", "أوفرول", "جوارب", "جورب شفاف", "شرابات", "حذاء", "سنيكرز", "حذاء رياضي", "بوت", "بوت كاحل", "صندل", "شبشب", "كعب عالي", "كعب", "باليرينا", "لوفر", "أوكسفورد", "شنطة", "شنطة يد", "شنطة ظهر", "توت باج", "كلتش", "كروس بودي", "محفظة", "حزام", "ربطة عنق", "وشاح", "قفازات", "قبعة", "كاب", "نظارة شمسية", "ساعة", "مجوهرات", "عقد", "سوار", "خاتم", "حلق", "عطر", "كولونيا", "ميك أب", "أحمر شفاه", "لمع شفاه", "كريم أساس", "ماسكارا", "آيلاينر", "ظل عيون", "بلاشر", "هايلايتر", "كونسيلر", "برايمر", "فيكس سبري", "كريم", "لوشن", "سيروم", "تونر", "مرطب", "واقي شمس", "شامبو", "بلسم", "ماسك", "صابون", "فرشاة", "هاتف", "آيفون", "سامسونج", "لاب توب", "كمبيوتر", "تابلت", "آيباد", "أيربودز", "سماعات رأس", "سماعات أذن", "كاميرا", "تلفزيون", "شاشة", "كيبورد", "ماوس", "شاحن", "كيبل", "باور بنك", "بطارية", "ساعة ذكية", "سماعة", "راوتر", "ثلاجة", "غسالة", "مكنسة كهربائية", "مكيف", "دفاية", "مروحة", "خلاط", "عجانة", "فرن", "مايكرويف", "محمصة", "غلاية", "ماكينة قهوة", "مكواة", "مجفف شعر", "كرسي", "طاولة", "مكتب", "سرير", "كنبة", "لمبة", "مرآة", "سجادة", "ستارة", "مخدة", "جهاز مشي", "دمبل", "حصيرة يوغا", "دراجة", "كرة", "جيم"}
    color_keywords = {"أسود", "أبيض", "أحمر", "أزرق", "أخضر", "أصفر", "وردي", "بنفسجي", "برتقالي", "بني", "بيج", "رمادي", "كحلي", "عنابي", "زيتي", "كاكي", "كريمي", "عاجي", "ذهبي", "فضي", "روز جولد", "متعدد الألوان", "سادة", "مطبوع", "زهري", "مخطط", "مربعات", "منقط", "تاي داي", "تمويه", "تدرج لوني"}
    material_keywords = {"جينز", "جلد", "شمواه", "مخمل", "ساتان", "حرير", "قطن", "كتان", "صوف", "محبوك", "شبك", "دانتيل", "شيفون", "أورجانزا", "ترتر"}
    fit_keywords = {"ضيق", "عادي", "واسع", "سكيني", "مستقيم", "رجل واسعة", "منفوش", "بوت كت", "قصير", "ميني", "ميدي", "ماكسي", "خصر عالي", "خصر منخفض", "ضيق", "قصة A", "ببلوم", "لف", "اكتاف مكشوفة", "كتف واحد", "كتف مكشوف", "غير متناظر", "متعدد الطبقات"}
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
    
    # نبني الجملة
    parts = []
    
    # 1. نوع المنتج (آخر نوع لقيناه عشان يكون الأدق)
    if types:
        parts.append(types[-1])
    
    # 2. الجنس
    gender_word = {"female": "نسائي", "male": "رجالي", "kids": "أطفال", "neutral": ""}
    if gender in gender_word and gender_word[gender]:
        parts.append(gender_word[gender])
    
    # 3. لون/خامة/قصة
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
        # ناخد أول تفصيلين بس
        desc_parts.extend(details[:2])
    
    if desc_parts:
        parts.extend(desc_parts)
    
    # ندمج
    result = " ".join(parts)
    
    # تنظيف نهائي
    result = re.sub(r'\s+', ' ', result).strip()
    
    return result if result else "منتج مميز"


def summarize_product(title):
    gender = detect_gender(title)
    keywords = extract_keywords(title)
    return build_description(keywords, gender)


def translate_to_arabic(text):
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {"client": "gtx", "sl": "en", "tl": "ar", "dt": "t", "q": text}
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        r = requests.get(url, params=params, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            translated = ""
            for item in data[0]:
                if item[0]:
                    translated += item[0]
            return translated if translated else text
    except Exception as e:
        print(f"Translation error: {e}")
    return text


# ─── قوالب راقية ───
TEMPLATES_DB = {
    "fashion": {
        "female": [
            "{product} بتصميم يبرز الأناقة بأسلوب راقي ✨",
            "قطعة أنيقة تناسب مختلف المناسبات 💫\n\n{product}",
            "تصميم ناعم يلبي احتياجاتك اليومية بأناقة 🤍\n\n{product}",
            "{product} — اختيار يجمع بين الجودة والأناقة",
            "لمسة أنثوية راقية مع {product} ✨",
            "تفاصيل دقيقة وتصميم يخطف الأنظار 👀\n\n{product}",
            "{product} يضيف لمسة من الفخامة لإطلالتك",
            "أناقة بسيطة مع {product} — مناسب لكل الأوقات 💎",
            "تصميم عصري يناسب الذوق الرفيع ✨\n\n{product}",
            "{product} — جودة عالية بتصميم يدوم",
        ],
        "male": [
            "{product} بتصميم كلاسيكي يناسب الرجل الأنيق",
            "قطعة عملية بأسلوب راقي 💼\n\n{product}",
            "تصميم عملي يلبي احتياجاتك اليومية بأناقة 🤍\n\n{product}",
            "{product} — اختيار يجمع بين الجودة والعملية",
            "لمسة رجالية أنيقة مع {product} ✨",
            "تفاصيل دقيقة وتصميم عملي 👔\n\n{product}",
            "{product} يضيف لمسة من الأناقة لإطلالتك",
            "أناقة بسيطة مع {product} — مناسب لكل الأوقات 💎",
            "تصميم عصري يناسب الذوق الرفيع ✨\n\n{product}",
            "{product} — جودة عالية بتصميم يدوم",
        ],
        "kids": [
            "{product} بتصميم عملي وأنيق للأطفال",
            "قطعة مريحة تناسب نشاطاتهم اليومية 🧸\n\n{product}",
            "تصميم آمن وأنيق يلبي احتياجات طفلك 🤍\n\n{product}",
            "{product} — اختيار يجمع بين الراحة والجودة",
            "لمسة ظريفة وأنيقة مع {product} ✨",
            "تفاصيل مدروسة تناسب الأطفال 👶\n\n{product}",
            "{product} يضيف لمسة من المرح لإطلالة طفلك",
            "راحة وأناقة مع {product} — مناسب للألعاب والخروج 💎",
            "تصميم عصري يناسب أصغر الأذواق ✨\n\n{product}",
            "{product} — جودة عالية تتحمل الحركة والمرح",
        ],
        "neutral": [
            "{product} بتصميم عصري يناسب مختلف الأذواق",
            "قطعة عملية بأسلوب راقي ✨\n\n{product}",
            "تصميم عملي يلبي احتياجاتك اليومية 🤍\n\n{product}",
            "{product} — اختيار يجمع بين الجودة والعملية",
            "تفاصيل دقيقة وتصميم أنيق ✨\n\n{product}",
            "{product} يضيف لمسة من الأناقة لمساحتك",
            "أناقة بسيطة مع {product} — مناسب لكل الأوقات 💎",
            "تصميم عصري يناسب الذوق الرفيع ✨\n\n{product}",
            "{product} — جودة عالية بتصميم يدوم",
        ],
    },
    "accessories": {
        "female": [
            "{product} — إكسسوار يكمل إطلالتك بأناقة",
            "تفصيلة راقية تضيف لمسة مميزة ✨\n\n{product}",
            "تصميم ناعم يناسب مختلف الأوقات 🤍\n\n{product}",
            "{product} — قطعة عملية بأسلوب أنيق",
            "لمسة من الفخامة مع {product} 💎",
            "إكسسوار أنيق يبرز ذوقك الرفيع ✨\n\n{product}",
            "{product} بتصميم يجمع بين الجمال والعملية",
            "قطعة مميزة تستحق الاهتمام 👌\n\n{product}",
        ],
        "male": [
            "{product} — إكسسوار يكمل إطلالتك بأناقة",
            "تفصيلة راقية تضيف لمسة مميزة ✨\n\n{product}",
            "تصميم عملي يناسب مختلف الأوقات 🤍\n\n{product}",
            "{product} — قطعة عملية بأسلوب أنيق",
            "لمسة من الأناقة مع {product} 💎",
            "إكسسوار أنيق يبرز ذوقك الرفيع ✨\n\n{product}",
            "{product} بتصميم يجمع بين الجودة والعملية",
            "قطعة مميزة تستحق الاهتمام 👌\n\n{product}",
        ],
        "kids": [
            "{product} — إكسسوار ظريف للأطفال",
            "تصميم آمن وأنيق يناسب صغارك 🧸\n\n{product}",
            "قطعة عملية تضيف لمسة من المرح 🤍\n\n{product}",
            "{product} — اختيار يلبي احتياجات طفلك",
            "لمسة ظريفة مع {product} 💎",
            "إكسسوار أنيق يناسب نشاطاتهم اليومية ✨\n\n{product}",
            "{product} بتصميم يجمع بين الأمان والأناقة",
            "قطعة مميزة تستحق الاهتمام 👌\n\n{product}",
        ],
        "neutral": [
            "{product} — إكسسوار يكمل إطلالتك بأناقة",
            "تفصيلة راقية تضيف لمسة مميزة ✨\n\n{product}",
            "تصميم عملي يناسب مختلف الأوقات 🤍\n\n{product}",
            "{product} — قطعة عملية بأسلوب أنيق",
            "لمسة من الأناقة مع {product} 💎",
            "إكسسوار أنيق يبرز ذوقك الرفيع ✨\n\n{product}",
            "{product} بتصميم يجمع بين الجودة والعملية",
            "قطعة مميزة تستحق الاهتمام 👌\n\n{product}",
        ],
    },
    "beauty": {
        "female": [
            "{product} — منتج عناية بجودة عالية",
            "تركيبة فاخرة تعطي نتائج مميزة ✨\n\n{product}",
            "منتج يستحق التجربة لمفعوله الفعّال 💎\n\n{product}",
            "{product} — اختيار يلبي احتياجاتك بأناقة",
            "عناية يومية بأسلوب راقي مع {product} 🌸",
            "جودة تلاحظينها من أول استخدام ✨\n\n{product}",
            "{product} — سر الإشراقة الطبيعية",
            "منتج فعّال بتجربة مريحة 👌\n\n{product}",
        ],
        "male": [
            "{product} — منتج عناية بجودة عالية",
            "تركيبة فاخرة تعطي نتائج مميزة ✨\n\n{product}",
            "منتج يستحق التجربة لمفعوله الفعّال 💎\n\n{product}",
            "{product} — اختيار يلبي احتياجاتك بأناقة",
            "عناية يومية بأسلوب راقي مع {product} 🌸",
            "جودة تلاحظها من أول استخدام ✨\n\n{product}",
            "{product} — سر الأناقة الطبيعية",
            "منتج فعّال بتجربة مريحة 👌\n\n{product}",
        ],
        "kids": [
            "{product} — منتج عناية آمن للأطفال",
            "تركيبة لطيفة تناسب بشرتهم الحساسة ✨\n\n{product}",
            "منتج يستحق التجربة لراحة طفلك 💎\n\n{product}",
            "{product} — اختيار يلبي احتياجات طفلك",
            "عناية يومية بأسلوب آمن مع {product} 🌸",
            "جودة ملحوظة من أول استخدام ✨\n\n{product}",
            "{product} — سر النعومة والنظافة",
            "منتج فعّال بتجربة مريحة 👌\n\n{product}",
        ],
        "neutral": [
            "{product} — منتج عناية بجودة عالية",
            "تركيبة فاخرة تعطي نتائج مميزة ✨\n\n{product}",
            "منتج يستحق التجربة لمفعوله الفعّال 💎\n\n{product}",
            "{product} — اختيار يلبي احتياجاتك",
            "عناية يومية بأسلوب راقي مع {product} 🌸",
            "جودة تلاحظها من أول استخدام ✨\n\n{product}",
            "{product} — سر الإشراقة الطبيعية",
            "منتج فعّال بتجربة مريحة 👌\n\n{product}",
        ],
    },
    "home": {
        "neutral": [
            "{product} — لمسة أنيقة تكمل ديكور منزلك",
            "تصميم عملي بأسلوب راقي ✨\n\n{product}",
            "جودة تتحمل الاستخدام اليومي بأريحية 🏠\n\n{product}",
            "{product} — اختيار يجمع بين الجمال والعملية",
            "لمسة من الفخامة لمساحتك مع {product} 💎",
            "تفاصيل مدروسة بتصميم عصري ✨\n\n{product}",
            "{product} — عملي وأنيق في آن واحد",
            "قطعة تستحق الاهتمام لمنزلك 👌\n\n{product}",
        ],
    },
    "electronics": {
        "neutral": [
            "{product} — تقنية حديثة بأداء ممتاز",
            "تصميم عملي يسهل الاستخدام اليومي ⚡\n\n{product}",
            "جودة عالية تدوم معك طويلاً 📱\n\n{product}",
            "{product} — اختيار يجمع بين القوة والأناقة",
            "أداء مميز بتجربة سلسة مع {product} 💎",
            "تقنية موثوقة بتصميم عصري ✨\n\n{product}",
            "{product} — استثمار يستحق الثقة",
            "جهاز فعّال يلبي احتياجاتك 👌\n\n{product}",
        ],
    },
    "sports": {
        "neutral": [
            "{product} — أداء مميز لتحقيق أهدافك",
            "تصميم مريح يناسب التمارين المكثفة 💪\n\n{product}",
            "جودة عالية تتحمل الاستخدام اليومي ✨\n\n{product}",
            "{product} — اختيار يجمع بين القوة والراحة",
            "أداء ممتاز بتجربة مريحة مع {product} 💎",
            "تصميم عملي يسهل حركتك ✨\n\n{product}",
            "{product} — استثمار في صحتك ولياقتك",
            "معدات موثوقة لتمارينك اليومية 👌\n\n{product}",
        ],
    },
    "general": {
        "female": [
            "{product} — منتج بجودة تستحق الاهتمام",
            "تصميم راقي يناسب احتياجاتك ✨\n\n{product}",
            "قطعة مميزة بتفاصيل مدروسة 💎\n\n{product}",
            "{product} — اختيار يجمع بين الأناقة والجودة",
            "جودة عالية بتجربة مريحة 🤍\n\n{product}",
        ],
        "male": [
            "{product} — منتج بجودة تستحق الاهتمام",
            "تصميم راقي يناسب احتياجاتك ✨\n\n{product}",
            "قطعة مميزة بتفاصيل مدروسة 💎\n\n{product}",
            "{product} — اختيار يجمع بين الأناقة والجودة",
            "جودة عالية بتجربة مريحة 🤍\n\n{product}",
        ],
        "kids": [
            "{product} — منتج بجودة تستحق الاهتمام",
            "تصميم راقي يناسب احتياجات طفلك ✨\n\n{product}",
            "قطعة مميزة بتفاصيل مدروسة 💎\n\n{product}",
            "{product} — اختيار يجمع بين الأمان والجودة",
            "جودة عالية بتجربة مريحة 🤍\n\n{product}",
        ],
        "neutral": [
            "{product} — منتج بجودة تستحق الاهتمام",
            "تصميم راقي يناسب احتياجاتك ✨\n\n{product}",
            "قطعة مميزة بتفاصيل مدروسة 💎\n\n{product}",
            "{product} — اختيار يجمع بين الأناقة والجودة",
            "جودة عالية بتجربة مريحة 🤍\n\n{product}",
        ],
    },
}


def get_templates(category, gender, product_name):
    global _last_used_templates
    cat_data = TEMPLATES_DB.get(category, TEMPLATES_DB["general"])
    
    if isinstance(cat_data, list):
        templates = cat_data
    else:
        templates = cat_data.get(
            gender, 
            cat_data.get("neutral", cat_data.get("female", list(cat_data.values())[0]))
        )
    
    key = f"{category}_{gender}"
    last_used = _last_used_templates.get(key)
    
    available = [t for t in templates if t != last_used]
    if not available:
        available = templates
    
    template = random.choice(available)
    _last_used_templates[key] = template
    
    return template.format(product=product_name)


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
                print(f"  Waiting {delay:.1f}s before retry...")
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
                "sec-ch-ua": "\"Not_A Brand\";v=\"8\", \"Chromium\";v=\"120\", \"Google Chrome\";v=\"120\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"Windows\"",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "cross-site",
                "Sec-Fetch-User": "?1",
                "Priority": "u=0, i",
            }

            proxies = {}
            if PROXY_URL:
                proxies = {"http": PROXY_URL, "https": PROXY_URL}

            r = session.get(url, headers=headers, timeout=15, proxies=proxies, allow_redirects=True)
            print(f"Attempt {attempt + 1}: Status {r.status_code}, Length {len(r.text)}")

            if r.status_code != 200:
                continue
            if len(r.text) < 3000:
                print(f"  Content too short ({len(r.text)} chars)")
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
                print("  Title not found")
                continue

            category = detect_product_category(title)
            gender = detect_gender(title)
            print(f"  SUCCESS: category={category}, gender={gender}, title={title[:40]}...")

            return {
                "category": category,
                "gender": gender,
                "full_title": title,
                "image": image,
            }

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            continue

    print("  All attempts failed")
    return None


def generate_post(product_data, original_url):
    category = product_data.get("category", "general")
    gender = product_data.get("gender", "neutral")
    title = product_data.get("full_title", "")

    # ← الجديد: نستخرج وصف منظم من الكلمات المفتاحية
    product_name = summarize_product(title)

    post = get_templates(category, gender, product_name)
    post += "\n\n🛒 رابط الشراء:\n" + original_url

    return post


@bot.message_handler(func=lambda m: True)
def handler(msg):
    text = msg.text.strip()
    urls = re.findall(r"https?://\S+", text)

    if not urls:
        bot.reply_to(msg, "❌ يرجى إرسال رابط المنتج من شي إن")
        return

    for original_url in urls:
        print("\n" + "="*50)
        print(f"Processing: {original_url}")

        if not is_shein_url(original_url):
            bot.reply_to(msg, "❌ الرابط يجب أن يكون من shein.com")
            continue

        wait = bot.reply_to(msg, "⏳ جاري تحليل المنتج وتجهيز المنشور...")

        product = get_shein_product(original_url)

        if not product:
            bot.edit_message_text("❌ تعذر قراءة بيانات المنتج", msg.chat.id, wait.message_id)
            continue

        post = generate_post(product, original_url)

        try:
            if product["image"]:
                bot.send_photo(msg.chat.id, product["image"], caption=post, parse_mode="Markdown")
            else:
                bot.send_message(msg.chat.id, post, parse_mode="Markdown")
            bot.delete_message(msg.chat.id, wait.message_id)
        except Exception as e:
            print(f"Error sending: {e}")
            try:
                bot.send_message(msg.chat.id, post, parse_mode="Markdown")
                bot.delete_message(msg.chat.id, wait.message_id)
            except Exception as e2:
                print(f"Error sending text: {e2}")
                bot.edit_message_text("❌ حدث خطأ في الإرسال", msg.chat.id, wait.message_id)


from flask import Flask, request

app = Flask(__name__)

WEBHOOK_HOST = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
WEBHOOK_PORT = int(os.environ.get("PORT", 10000))
WEBHOOK_URL_BASE = f"https://{WEBHOOK_HOST}" if WEBHOOK_HOST else None
WEBHOOK_URL_PATH = f"/webhook/{TOKEN}"

@app.route("/")
def index():
    return "🤖 البوت يعمل — شي إن ديلز 🔥"

@app.route(WEBHOOK_URL_PATH, methods=["POST"])
def webhook():
    if request.headers.get("content-type") == "application/json":
        json_string = request.get_data().decode("utf-8")
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ""
    else:
        return "Unsupported Media Type", 415

def start_webhook():
    if WEBHOOK_HOST:
        bot.remove_webhook()
        time.sleep(1)
        bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH)
        print(f"✅ Webhook set to: {WEBHOOK_URL_BASE}{WEBHOOK_URL_PATH}")
    else:
        print("⚠️ RENDER_EXTERNAL_HOSTNAME not set, running in local mode...")

    app.run(host="0.0.0.0", port=WEBHOOK_PORT)

if __name__ == "__main__":
    start_webhook()
