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

FEMALE_KEYWORDS = [
    "women", "woman", "ladies", "lady", "female", "girl", "girls", "feminine",
    "bride", "bridal", "wedding", "maternity", "lingerie", "bra", "panty", "panties",
    "tights", "leggings women", "heels", "flats women", "handbag", "clutch", "tote",
    "crossbody", "sling", "makeup", "lipstick", "mascara", "eyeliner", "foundation",
    "skincare women", "haircare women", "perfume women", "fragrance women",
    "earring", "necklace women", "bracelet women", "hair clip", "headband",
    "scrunchie", "yoga mat women", "bag women", "dress", "skirt", "blouse",
    "bodysuit", "romper", "jumpsuit", "cardigan women", "trench women"
]

MALE_KEYWORDS = [
    "men", "man", "male", "gentleman", "gentlemen", "boys", "boy", "masculine",
    "suit", "blazer", "tie", "bow tie", "cufflinks", "suspenders", "vest",
    "trousers", "chinos", "cargo pants", "shorts men", "polo", "henley",
    "undershirt", "boxer", "briefs", "trunks", "socks men", "belt men",
    "wallet men", "watch men", "bracelet men", "ring men", "necklace men",
    "backpack men", "bag men", "duffle", "briefcase", "messenger bag",
    "shaving", "razor", "aftershave", "cologne", "perfume men", "fragrance men",
    "beard", "mustache", "haircare men", "skincare men", "deodorant men"
]


def detect_product_category(product_name):
    name_lower = product_name.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in name_lower:
                return category
    return "general"


def detect_gender(title):
    title_lower = title.lower()
    female_score = sum(1 for kw in FEMALE_KEYWORDS if kw in title_lower)
    male_score = sum(1 for kw in MALE_KEYWORDS if kw in title_lower)
    if female_score > male_score:
        return "female"
    elif male_score > female_score:
        return "male"
    return "neutral"


def summarize_product(title, category):
    """
    يلخص اسم المنتج من العنوان:
    1. يترجم العنوان للعربي
    2. يشيل كلمات SHEIN والأرقام والمقاسات
    3. يختصر لأهم 4-6 كلمات
    4. يضيف وصف الجنس لو واضح
    """
    # ترجمة العنوان
    translated = translate_to_arabic(title)
    
    # تنظيف: شيل كلمات ماركات ومواقع وكلمات مش مهمة
    cleaned = re.sub(r'\bSHEIN\b|\bAmazon\b|\bAliExpress\b|\beBay\b|\bWish\b', '', translated, flags=re.IGNORECASE)
    cleaned = re.sub(r'\b\d+\s*(ml|g|kg|cm|mm|inch|inches)\b', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\b(USD|EUR|GBP|SAR|AED)\s*\d+\b', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\b\d{1,2}%?\s*off?\b', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'[\(\)\[\]\{\}]', '', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    # لو العنوان طويل، اختصره لأهم كلمات
    words = cleaned.split()
    if len(words) > 6:
        # خد أول 6 كلمات (عادة بتكون أهم حاجة)
        cleaned = ' '.join(words[:6])
    
    # لو العنوان فاضي بعد التنظيف، رجع ترجمة مختصرة
    if not cleaned or len(cleaned) < 3:
        words = translated.split()
        cleaned = ' '.join(words[:5])
    
    # ضيف وصف الجنس
    gender = detect_gender(title)
    gender_word = ""
    if gender == "female":
        gender_word = "نسائي"
    elif gender == "male":
        gender_word = "رجالي"
    
    # رتب: لو فيه gender، حطه في الآخر
    if gender_word and gender_word not in cleaned:
        cleaned = f"{cleaned} {gender_word}"
    
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


# ─── قوالب راقية حسب الجنس ───
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
        templates = cat_data.get(gender, cat_data.get("neutral", cat_data.get("female", list(cat_data.values())[0])))
    
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

    # ← الجديد: نلخص اسم المنتج من العنوان كله
    product_name = summarize_product(title, category)

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
