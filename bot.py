import telebot
import re
import time
import random
import os
import requests
from bs4 import BeautifulSoup

TOKEN = "8888709197:AAEVCTpVticEzi-NBaWRdIQDmKJSxdRzA54"
bot = telebot.TeleBot(TOKEN)

PROXY_URL = os.environ.get("PROXY_URL")


CATEGORY_KEYWORDS = {
    "electronics": ["phone", "iphone", "samsung", "laptop", "computer", "tablet", "ipad", "airpods", "headphones", "camera", "tv", "screen", "monitor", "keyboard", "mouse", "charger", "cable", "power bank", "battery", "smart watch", "watch", "speaker", "router", "modem", "electronic", "digital"],
    "fashion": ["shirt", "t-shirt", "pants", "jeans", "jacket", "hoodie", "dress", "skirt", "socks", "shoes", "sneakers", "boots", "sandals", "slippers", "cap", "hat", "bag", "backpack", "wallet", "belt", "tie", "scarf", "gloves", "clothing", "apparel", "wear", "fashion", "top", "blouse", "bodysuit", "romper", "jumpsuit", "cardigan", "sweater", "coat", "trench"],
    "beauty": ["perfume", "fragrance", "oud", "musk", "cream", "lotion", "shampoo", "conditioner", "soap", "makeup", "lipstick", "foundation", "mascara", "eyeliner", "brush", "cosmetic", "skincare", "haircare"],
    "home": ["refrigerator", "fridge", "washing machine", "vacuum cleaner", "air conditioner", "ac", "heater", "fan", "blender", "mixer", "oven", "microwave", "toaster", "kettle", "coffee maker", "iron", "hair dryer", "chair", "table", "desk", "bed", "sofa", "couch", "lamp", "light", "mirror", "carpet", "curtain", "furniture", "kitchen", "home", "house", "decor", "wall", "storage", "organizer"],
    "sports": ["treadmill", "dumbbell", "yoga mat", "bicycle", "ball", "gym", "fitness", "exercise", "workout", "sport", "running", "walking", "training", "sneakers", "shoes"],
    "accessories": ["bag", "backpack", "wallet", "belt", "tie", "scarf", "gloves", "hat", "cap", "sunglasses", "watch", "jewelry", "necklace", "bracelet", "ring", "earring", "hair clip", "headband"],
}


def detect_product_category(product_name):
    name_lower = product_name.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in name_lower:
                return category
    return "general"


def get_category_emoji(category):
    emojis = {"electronics": "📱", "fashion": "👗", "beauty": "💄", "home": "🏠", "sports": "💪", "accessories": "👜", "general": "🛍️"}
    return emojis.get(category, "🛍️")


def shorten_title(title):
    words = title.split()
    short = " ".join(words[:10])
    if len(short) > 80:
        short = short[:77] + "..."
    return short


def get_templates(category, title_short):
    fashion_templates = [
        "يااااا زين {product} 🩵\n\nتفصيلته تبرز الجسم بطريقة ناعمة وأنيقة ✨",
        "{product} ..\n\nمرة مناسبة للدوامات والاجتماعات والمناسبات الرسمية 👌",
        "تفاصيييييل {product} رووووعة 😮‍💨🤍\n\nمو من فراغ صارت من الأكثر مبيعًا 🏆",
        "إذا ناوية سفر وتدورين قطعة ساترة وشييييك، فلا يفووووتك أبد! ✨\n\n{product}",
        "من أكثر التفاصيل اللي تعطي اللوك لمسة أنثوية؟ ✨\n\n{product} 💫",
        "وش أمدح أول؟ 😍\n\nجمال {product} ولا قصته الأنيقة؟ ✨\n\nاللوك كله شيك 💫",
        "{product} ✨\n\nاللون والقصة كلها أنثوية بشكل يلفت 👀💫",
        "يا بنات {product} يستاهل التجربة 🔥\n\nمن القطع اللي ما تستغنين عنها أبد ✨",
    ]
    
    accessories_templates = [
        "{product} رهيبببة وحجمها عملي 👌\n\nأكثر شيء شدني فيها التفاصيل المميزة 🤍",
        "بناااات لا تستهينون بـ {product} ✨\n\nحقيقي يغيّر اللوك بالكامل! 👌",
        "تنططططق على اليد يابنات، ولوكها أنثوي وأنيق بشكل يلفت ✨\n\n{product}",
        "{product} ✨\n\nمن الإكسسوارات اللي أشوفها ضرورية بكل دولاب 👌",
        "يااااا زين {product} 🤍\n\nتكمل أي لوك وتعطيه لمسة فخامة ✨",
    ]
    
    home_templates = [
        "{product} ✨\n\nلمسة فخامة تكمل ديكور بيتك وتخليه أجمل 🏠",
        "يااااا زين {product} في البيت 🤍\n\nعملي وجميل بنفس الوقت ✨",
        "{product} يستاهل التجربة 🔥\n\nجودة تتحمل الاستخدام اليومي بكل أريحية ✨",
        "من الأشياء اللي تسوى كل ريال 💎\n\n{product} ✨",
    ]
    
    beauty_templates = [
        "{product} يعطيكي إشراقة طبيعية ✨\n\nجودة عالية ونتيجة تبهر 💄",
        "يااااا زين {product} 🌸\n\nرائحة تدوم وإحساس منعش طول اليوم ✨",
        "{product} ✨\n\nاختيارك الأفضل للعناية بنفسك وبأسلوبك 💎",
    ]
    
    electronics_templates = [
        "{product} 📱\n\nتقنية حديثة وأداء ممتاز يستاهل الاستثمار ✨",
        "{product} ⚡\n\nسهل الاستخدام ويعيش معاك طويل 🔥",
    ]
    
    sports_templates = [
        "{product} 💪\n\nيساعدك على تحقيق أهدافك الرياضية بكل قوة ✨",
        "{product} ✨\n\nمريح وعملي للتمارين اليومية 🔥",
    ]
    
    general_templates = [
        "{product} ✨\n\nمنتج مميز وجودته تتكلم عن نفسها 🔥",
        "{product} 💎\n\nمن الأشياء اللي تسوى كل ريال والتجربة ✨",
        "يااااا زين {product} 🤍\n\nيستاهل التجربة بكل تأكيد ✨",
        "{product} ✨\n\nلا تفوتي الفرصة واختاري الأفضل 💫",
    ]
    
    templates_map = {
        "fashion": fashion_templates,
        "accessories": accessories_templates,
        "home": home_templates,
        "beauty": beauty_templates,
        "electronics": electronics_templates,
        "sports": sports_templates,
        "general": general_templates,
    }
    
    templates = templates_map.get(category, general_templates)
    template = random.choice(templates)
    return template.format(product=title_short)


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
            print(f"  SUCCESS: category={category}, title={title[:40]}...")
            
            return {
                "category": category,
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
    title = product_data.get("full_title", "")
    title_short = shorten_title(title)
    
    post = get_templates(category, title_short)
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
