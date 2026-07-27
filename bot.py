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

# لتتبع آخر template
_last_used_templates = {}

CATEGORY_KEYWORDS = {
    "electronics": ["phone", "iphone", "samsung", "laptop", "computer", "tablet", "ipad", "airpods", "headphones", "camera", "tv", "screen", "monitor", "keyboard", "mouse", "charger", "cable", "power bank", "battery", "smart watch", "watch", "speaker", "router", "modem", "electronic", "digital", "bluetooth", "wireless", "usb", "hdmi"],
    "fashion": ["shirt", "t-shirt", "pants", "jeans", "jacket", "hoodie", "dress", "skirt", "socks", "shoes", "sneakers", "boots", "sandals", "slippers", "cap", "hat", "bag", "backpack", "wallet", "belt", "tie", "scarf", "gloves", "clothing", "apparel", "wear", "fashion", "top", "blouse", "bodysuit", "romper", "jumpsuit", "cardigan", "sweater", "coat", "trench", "denim", "cotton", "linen", "wool", "silk"],
    "beauty": ["perfume", "fragrance", "oud", "musk", "cream", "lotion", "shampoo", "conditioner", "soap", "makeup", "lipstick", "foundation", "mascara", "eyeliner", "brush", "cosmetic", "skincare", "haircare", "serum", "toner", "moisturizer", "sunscreen", "mask"],
    "home": ["refrigerator", "fridge", "washing machine", "vacuum cleaner", "air conditioner", "ac", "heater", "fan", "blender", "mixer", "oven", "microwave", "toaster", "kettle", "coffee maker", "iron", "hair dryer", "chair", "table", "desk", "bed", "sofa", "couch", "lamp", "light", "mirror", "carpet", "curtain", "furniture", "kitchen", "home", "house", "decor", "wall", "storage", "organizer", "pillow", "blanket"],
    "sports": ["treadmill", "dumbbell", "yoga mat", "bicycle", "ball", "gym", "fitness", "exercise", "workout", "sport", "running", "walking", "training", "sneakers", "shoes", "dumbbells", "kettlebell", "resistance band", "foam roller"],
    "accessories": ["bag", "backpack", "wallet", "belt", "tie", "scarf", "gloves", "hat", "cap", "sunglasses", "watch", "jewelry", "necklace", "bracelet", "ring", "earring", "hair clip", "headband", "sunglasses", "umbrella", "keychain"],
}

# ─── كلمات تحديد الجنس والفئة العمرية ───
# كل كلمة ليها وزن: كلما زاد الوزن، كلما كانت أكثر تحديداً

KIDS_KEYWORDS = {
    # كلمات مؤكدة للأطفال (أولوية قصوى)
    "kids": 10, "children": 10, "child": 10, "baby": 10, "toddler": 10,
    "infant": 10, "newborn": 10, "youth": 8, "teen": 5,
    # ملابس أطفال شائعة
    "onesie": 8, "bib": 8, "diaper": 8, "stroller": 8, "crib": 8,
    "pacifier": 8, "feeding bottle": 8,
}

FEMALE_KEYWORDS = {
    # كلمات مؤكدة نسائية
    "women": 10, "woman": 10, "ladies": 10, "lady": 10, "female": 10,
    "womens": 10, "women's": 10,
    # ملابس نسائية مميزة
    "dress": 8, "frock": 8, "gown": 8, "skirt": 8, "blouse": 7,
    "bodysuit women": 8, "romper women": 8, "jumpsuit women": 8,
    "lingerie": 10, "bra": 10, "panty": 10, "panties": 10,
    "tights": 7, "leggings women": 7, "legging women": 7,
    "heels": 8, "high heels": 10, "stiletto": 10, "pump": 8,
    "handbag": 8, "clutch": 8, "tote bag": 8, "crossbody": 7,
    "maternity": 10, "bride": 9, "bridal": 9, "wedding dress": 10,
    # ميك أب وعناية نسائية
    "makeup": 8, "lipstick": 8, "mascara": 8, "eyeliner": 8,
    "foundation": 7, "skincare women": 7, "haircare women": 7,
    "perfume women": 7, "fragrance women": 7,
    # إكسسوارات نسائية
    "earring": 7, "necklace women": 7, "bracelet women": 7,
    "hair clip": 7, "headband": 6, "scrunchie": 8,
    # كلمات سياقية
    "feminine": 8, "girl's": 8, "girls'": 8,
}

MALE_KEYWORDS = {
    # كلمات مؤكدة رجالية
    "men": 10, "man": 10, "male": 10, "gentleman": 10, "gentlemen": 10,
    "mens": 10, "men's": 10,
    # ملابس رجالية مميزة
    "suit": 9, "blazer": 9, "tuxedo": 10, "vest men": 8,
    "bow tie": 9, "cufflinks": 10, "suspenders": 10,
    "trousers": 7, "chinos": 8, "cargo pants": 7,
    "polo shirt": 7, "henley": 8, "undershirt": 8,
    "boxer": 8, "briefs": 8, "trunks": 7,
    "socks men": 6, "belt men": 6,
    # عناية رجالية
    "shaving": 8, "razor": 8, "aftershave": 10, "cologne": 9,
    "perfume men": 7, "fragrance men": 7,
    "beard": 9, "mustache": 9, "haircare men": 7, "skincare men": 7,
    "deodorant men": 7,
    # إكسسوارات رجالية
    "wallet men": 6, "watch men": 6, "bracelet men": 6,
    "ring men": 6, "necklace men": 6,
    "backpack men": 6, "bag men": 6, "duffle": 7,
    "briefcase": 8, "messenger bag": 7, "tie": 8,
    # كلمات سياقية
    "masculine": 8, "boy's": 5, "boys'": 5,
}


def detect_product_category(product_name):
    name_lower = product_name.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in name_lower:
                return category
    return "general"


def detect_gender_and_age(title):
    """
    تحديد الجنس والفئة العمرية بدقة:
    - kids: أطفال
    - female: نسائي
    - male: رجالي
    - neutral: محايد / مش واضح
    """
    title_lower = title.lower()
    
    # 1) حساب النقاط لكل فئة
    kids_score = sum(weight for kw, weight in KIDS_KEYWORDS.items() if kw in title_lower)
    female_score = sum(weight for kw, weight in FEMALE_KEYWORDS.items() if kw in title_lower)
    male_score = sum(weight for kw, weight in MALE_KEYWORDS.items() if kw in title_lower)
    
    # 2) منطق خاص للكلمات اللي بتعتمد على السياق
    # "girls" لوحدها → نسائي، "girls" + "kids/children" → أطفال
    if "girls" in title_lower or "girl" in title_lower:
        if any(k in title_lower for k in ["kids", "children", "child", "baby", "toddler"]):
            kids_score += 5
        else:
            female_score += 4
    
    # "boys" لوحدها → رجالي، "boys" + "kids/children" → أطفال
    if "boys" in title_lower or "boy" in title_lower:
        if any(k in title_lower for k in ["kids", "children", "child", "baby", "toddler"]):
            kids_score += 5
        else:
            male_score += 4
    
    # 3) مقارنة النتائج
    scores = [("kids", kids_score), ("female", female_score), ("male", male_score)]
    scores.sort(key=lambda x: x[1], reverse=True)
    
    best, best_score = scores[0]
    second = scores[1][1]
    
    # لو الفارق كبير بين الأول والتاني، ناخد الأول
    if best_score > 0 and best_score >= second + 3:
        return best
    
    # لو مفيش نقاط خالص
    if best_score == 0:
        return "neutral"
    
    # لو الفارق صغير، نرجع neutral عشان ما نلخبطش
    return "neutral"


def summarize_product(title):
    """
    يلخص اسم المنتج من العنوان:
    1. يترجم العنوان للعربي
    2. يشيل كلمات SHEIN والأرقام والمقاسات والأسعار
    3. يختصر لأهم 5-6 كلمات
    4. يضيف وصف الجنس/العمر لو واضح
    """
    # ترجمة العنوان
    translated = translate_to_arabic(title)
    
    # تنظيف: شيل كلمات ماركات ومواقع وكلمات مش مهمة
    cleaned = re.sub(r'\bSHEIN\b|\bAmazon\b|\bAliExpress\b|\beBay\b|\bWish\b', '', translated, flags=re.IGNORECASE)
    cleaned = re.sub(r'\b\d+\s*(ml|g|kg|cm|mm|inch|inches|oz|lb|ltr)\b', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\b(USD|EUR|GBP|SAR|AED|QAR|KWD)\s*\d+[\.,]?\d*\b', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\b\d{1,2}%?\s*off?\b', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'[\(\)\[\]\{\}]', '', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    # لو العنوان طويل، اختصره لأهم كلمات
    words = cleaned.split()
    if len(words) > 6:
        cleaned = ' '.join(words[:6])
    
    # لو العنوان فاضي بعد التنظيف، رجع ترجمة مختصرة
    if not cleaned or len(cleaned) < 3:
        words = translated.split()
        cleaned = ' '.join(words[:5])
    
    # ضيف وصف الجنس/العمر
    gender_age = detect_gender_and_age(title)
    tag = ""
    if gender_age == "kids":
        tag = "أطفال"
    elif gender_age == "female":
        tag = "نسائي"
    elif gender_age == "male":
        tag = "رجالي"
    
    if tag and tag not in cleaned:
        cleaned = f"{cleaned} {tag}"
    
    return cleaned.strip()


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


# ─── قوالب راقية حسب الجنس والفئة ───
# {product} = اسم المنتج الملخص
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


def get_templates(category, gender_age, product_name):
    global _last_used_templates
    cat_data = TEMPLATES_DB.get(category, TEMPLATES_DB["general"])
    
    if isinstance(cat_data, list):
        templates = cat_data
    else:
        templates = cat_data.get(
            gender_age, 
            cat_data.get("neutral", cat_data.get("female", list(cat_data.values())[0]))
        )
    
    key = f"{category}_{gender_age}"
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
            gender_age = detect_gender_and_age(title)
            print(f"  SUCCESS: category={category}, gender_age={gender_age}, title={title[:40]}...")

            return {
                "category": category,
                "gender_age": gender_age,
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
    gender_age = product_data.get("gender_age", "neutral")
    title = product_data.get("full_title", "")

    product_name = summarize_product(title)

    post = get_templates(category, gender_age, product_name)
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
