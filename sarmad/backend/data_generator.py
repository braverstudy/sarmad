"""
Synthetic Reality Engine - Data Generator
Generates 2,500+ tweet objects with realistic time distributions
matching X API v2 schema.
"""

import random
import math
import uuid
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
import numpy as np

# Diverse creative display names (not just formal Arabic names)
CREATIVE_NAMES = [
    # Anime/Cartoon inspired (Arabic)
    "ناروتو العربي", "لوفي 🏴‍☠️", "غوكو السعودي", "كونان المحقق", "ايتاشي",
    "زورو", "ساسكي", "هينتا", "ميكاسا", "ليفاي", "إيرين", "سبايدر مان",
    
    # Science/Tech themed
    "كوانتم", "ذرة ⚛️", "نيوترون", "الكترون", "فوتون", "ثقب أسود 🕳️",
    "AI Master", "Tech Geek", "كود مبرمج", "هاكر أخلاقي", "DevOps",
    
    # Philosophical/Linguistic
    "فيلسوف مجهول", "حكيم الزمان", "أرسطو العرب", "ابن رشد", "فكر عميق",
    "لغوي متمرس", "نحوي", "بلاغي", "معجم عربي", "شاعر الحي",
    
    # Random creative Arabic
    "أبو فهد", "بو سعود", "عاشق القهوة ☕", "معلق رياضي", "خبير نفسي",
    "طباخ ماهر 👨‍🍳", "دكتور أسنان", "مهندس معماري", "رحالة 🌍", "غواص 🤿",
    "صقر الجزيرة 🦅", "ذئب البراري", "نمر", "أسد الصحراء", "فهد 🐆",
    
    # Random creative English/Mixed
    "Dark Knight", "Shadow", "Phoenix", "Storm", "Thunder ⚡",
    "مودي", "xxShadowxx", "GamerX", "ProPlayer", "ChampionKSA",
    "CryptoKing", "NFT Hunter", "Trader_SA", "StockMaster", "Bitcoin بيتكوين",
    
    # Aesthetic/Mood
    "سكون 🌙", "هدوء", "صمت", "وحدة", "أمل ✨", "حلم", "خيال",
    "مزاجي", "عفوي", "بسيط", "معقد", "غامض 🎭", "واضح", "صريح",
    
    # Food/Hobbies
    "محب الكبسة", "شاي وقهوة", "عاشق المكرونة 🍝", "برغر 🍔", "بيتزا",
    "Fitness 💪", "مشاء", "عداء", "سباح", "كرة قدم ⚽",
    
    # Meme/Humor
    "لا أفهم", "مش فاهم", "يا زلمة", "والله", "خلاص طفشت",
    "بدون اسم", "مجهول", "Anonymous", "NoName", "Just Me",
    "🤷", "😂", "💀", "🔥", "👀"
]

# Diverse usernames patterns
USERNAME_BASES_AR = [
    "abu", "om", "bnt", "wld", "x3li", "m7md", "3bd", "sa3d", "hmd",
    "fhd", "trki", "sltn", "rkan", "mshri", "nwf", "wld", "bdr"
]

USERNAME_BASES_EN = [
    "dark", "shadow", "night", "storm", "fire", "ice", "wolf", "lion",
    "hawk", "eagle", "king", "queen", "pro", "gamer", "hacker", "dev",
    "ninja", "samurai", "dragon", "phoenix", "ghost", "silent", "crypto"
]

USERNAME_BASES_ANIME = [
    "naruto", "sasuke", "goku", "luffy", "zoro", "eren", "levi", "mikasa",
    "itachi", "kakashi", "conan", "shinichi", "light", "ryuk", "gojo"
]

# Keywords for violation content
KEYWORDS_RELATED = ["مضاربة", "النسيم", "شرطة", "مشاجرة", "عنف", "مدرسة", "ضرب", "سلاح", "شوارع", "فيديو"]
KEYWORDS_NOISE = ["الهلال", "النصر", "مباراة", "موسم", "الرياض", "حفلة", "عروض", "تخفيضات"]

CROWD_TEMPLATES_WITH_KEYWORDS = [
    "يا ساتر وش ذا اللي صاير في {location}! مضاربة عنيفة 😱",
    "المقطع اللي منتشر عن {location} صراحة مخيف.. شرطة وينكم؟",
    "انتشر فيديو مضاربة في {location} والناس تتداوله بكثرة",
    "اللي صار في حي {location} اليوم شي ما يصدق.. مشاجرة بالسلاح 😰",
    "شوفوا المقطع اللي انتشر من {location}.. عنف غير طبيعي",
    "مضاربة {location} ترند الحين.. الله يستر",
    "الفيديو اللي من {location} وصلني اكثر من ٢٠ مرة",
    "حادثة {location} صارت حديث الناس.. شرطة الرياض تباشر",
    "وش السالفة في {location}؟ المقطع منتشر في كل مكان",
    "تداول واسع لمقطع مضاربة وقعت في حي {location}",
    "الله يستر قالوا في {location} صار شي.. المقطع مخيف",
    "مشاجرة عنيفة في {location} والفيديو منتشر",
    "شفت الفيديو؟ {location} صار فيها مضاربة شوارع قوية",
    "الحادثة اللي في {location} خطيرة.. فيديو واضح",
    "سمعت انه {location} فيها مشكلة كبيرة اليوم.. شرطة راحت"
]

CROWD_TEMPLATES_NOISE = [
    "اهم شي الهلال فاز اليوم 💙",
    "موسم الرياض نار هالسنة 🔥",
    "احد يعرف وين العروض الحين؟",
    "الجو اليوم حلو ماشاء الله",
    "وش رايكم في المطعم الجديد؟",
    "التخفيضات بدت في كل مكان",
    "مباراة الليلة مهمة جدا",
    "الحمدلله على كل حال",
    "صباح الخير للجميع ☀️",
    "وش اخبار السوق اليوم؟",
    "الله يوفق الجميع ان شاء الله",
    "متى اجازة نهاية الاسبوع؟"
]

REPLIES_TO_SOURCE = [
    "يا ساتر وش ذا!! 😱",
    "وينه مكان الحادثة؟",
    "الله يستر بس",
    "انشروا الفيديو لازم الناس تشوف",
    "شرطة وين انتوا؟!",
    "مخيف جداً 😰",
    "هذا في اي حي بالضبط؟",
    "الله يحفظنا واياكم",
    "تم البلاغ ان شاء الله",
    "وش صار بالضبط؟"
]


def generate_username() -> str:
    """Generate a diverse realistic Twitter username."""
    style = random.choice(["arabic", "english", "anime", "mixed", "numbers"])
    
    if style == "arabic":
        base = random.choice(USERNAME_BASES_AR)
        suffix = random.choice(["", str(random.randint(1, 999)), "_ksa", "_sa", "x", "xx"])
        prefix = random.choice(["", "x", "i_", "real_", ""])
    elif style == "english":
        base = random.choice(USERNAME_BASES_EN)
        suffix = random.choice(["", str(random.randint(1, 999)), "_x", "official", "real"])
        prefix = random.choice(["", "the", "its_", "im_", ""])
    elif style == "anime":
        base = random.choice(USERNAME_BASES_ANIME)
        suffix = random.choice(["_kun", "_san", str(random.randint(1, 99)), "_ar", "ksa"])
        prefix = random.choice(["", "x_", "real_", ""])
    elif style == "mixed":
        base = random.choice(USERNAME_BASES_AR + USERNAME_BASES_EN)
        suffix = str(random.randint(100, 9999))
        prefix = random.choice(["", "x", ""])
    else:
        base = random.choice(["user", "anon", "guest", "acc"])
        suffix = str(random.randint(10000, 99999))
        prefix = ""
    
    return f"@{prefix}{base}{suffix}"


def generate_display_name() -> str:
    """Generate a creative display name."""
    return random.choice(CREATIVE_NAMES)


# Daily normal content templates (these appear in For You)
DAILY_CONTENT_TEMPLATES = [
    # Food/Coffee
    "قهوة الصباح ☕ الحياة حلوة",
    "الفطور اليوم كان لذيذ جدا 😋",
    "احد يعرف مطعم زين في الرياض؟",
    "جربت مكان جديد للقهوة.. فخم!",
    "الكبسة السعودية ما يعلى عليها 🍚",
    
    # Work/Life
    "يوم عمل طويل.. الحمدلله على كل حال",
    "اجتماعات من الصبح 🙄",
    "اخيرا خلصت المشروع!",
    "التقاعد المبكر حلم 😂",
    "الدوام بكرة الله يعين",
    
    # Weather/General
    "الجو اليوم ماشاء الله رائع 🌤️",
    "حر شديد اليوم 🥵",
    "المطر نزل اخيرا! 🌧️",
    "الغبار يا ناس الغبار",
    "الشتاء قرب والله",
    
    # Entertainment
    "الفيلم الجديد كان قوي 🎬",
    "مسلسل جديد بديته.. حماس!",
    "الكتاب خلصته.. انصح فيه",
    "قيمز الليلة مع الشباب 🎮",
    "اليوتيوب اكل من وقتي",
    
    # Random thoughts
    "كيف الوقت يمر بسرعة",
    "الايام تمر بسرعة ماشاء الله",
    "احتاج اجازة طويلة 😩",
    "الحياة حلوة اذا تقدرها",
    "سبحان الله وبحمده",
    
    # Sports
    "مباراة اليوم كانت نار 🔥",
    "أهم شي الفوز 💪",
    "حظ اوفر للفريق المنافس",
    "الدوري السعودي تطور كثير",
    "تمرين الصباح خلص ✅",
    
    # Shopping
    "التخفيضات بدت.. محفظتي في خطر 😂",
    "وش افضل جوال الحين؟",
    "اشتريت لابتوب جديد 💻",
    "العروض نار بنده",
    "امازون وصل طلبي اخيرا 📦",
    
    # Questions
    "وش رايكم في موضوع...؟",
    "احد جرب هالشي قبل؟",
    "الناس يفضلون ايش اكثر؟",
    "سؤال: كيف تنظمون وقتكم؟",
    "محتار بين خيارين.. ساعدوني",
    
    # Tech
    "iOS ولا Android؟ 🤔",
    "الذكاء الاصطناعي مستقبل",
    "تطبيق جديد جربته.. ممتاز",
    "الانترنت بطيء اليوم",
    "ChatGPT غير كل شي 🤖"
]


def gaussian_random(mean: float, std_dev: float) -> float:
    """Generate a random number following Gaussian distribution."""
    return np.random.normal(mean, std_dev)


def log_normal_random(mu: float, sigma: float) -> float:
    """Generate a random number following Log-Normal distribution."""
    return np.random.lognormal(mu, sigma)


def generate_tweet_id() -> str:
    """Generate a realistic tweet ID."""
    return str(random.randint(1700000000000000000, 1799999999999999999))


def generate_user_id() -> str:
    """Generate a realistic user ID."""
    return str(random.randint(100000000, 9999999999))


def create_tweet(
    text: str,
    created_at: datetime,
    author_name: str,
    author_username: str,
    is_source: bool = False,
    has_video: bool = False,
    reply_to: str = None,
    conversation_id: str = None,
    reliability_score: float = None
) -> Dict[str, Any]:
    """Create a tweet object matching X API v2 schema."""
    
    tweet_id = generate_tweet_id()
    user_id = generate_user_id()
    
    # Extract hashtags from text
    hashtags = []
    words = text.split()
    for word in words:
        if word.startswith('#'):
            hashtags.append({"tag": word[1:]})
    
    tweet = {
        "id": tweet_id,
        "conversation_id": conversation_id or tweet_id,
        "author_id": user_id,
        "text": text,
        "created_at": created_at.isoformat() + "Z",
        "author": {
            "id": user_id,
            "username": author_username,
            "name": author_name,
            "reliability_score": reliability_score or round(random.uniform(0.3, 0.95), 2)
        },
        "entities": {
            "hashtags": hashtags,
            "mentions": []
        },
        "public_metrics": {
            "reply_count": random.randint(0, 50) if not is_source else random.randint(100, 500),
            "retweet_count": random.randint(0, 100) if not is_source else random.randint(200, 1000),
            "like_count": random.randint(0, 200) if not is_source else random.randint(500, 2000),
            "quote_count": random.randint(0, 20) if not is_source else random.randint(50, 200)
        },
        "is_source": is_source,
        "type": "source" if is_source else ("reply" if reply_to else "quote")
    }
    
    if has_video:
        tweet["media"] = [{
            "type": "video",
            "media_key": f"vid_{uuid.uuid4().hex[:8]}",
            "duration_ms": random.randint(15000, 120000)
        }]
    
    if reply_to:
        tweet["in_reply_to_user_id"] = reply_to
        tweet["type"] = "reply"
    
    return tweet


def generate_synthetic_dataset(base_time: datetime = None) -> List[Dict[str, Any]]:
    """
    Generate synthetic tweets based on settings.json configuration.
    """
    
    # Load settings
    settings = {
        "include_violated_content": True,
        "event_tweets_count": 2500,
        "daily_tweets_count": 1000,
        "violated_content_location": "النسيم"
    }
    
    try:
        settings_path = os.path.join(os.path.dirname(__file__), "settings.json")
        if os.path.exists(settings_path):
            with open(settings_path, "r", encoding="utf-8") as f:
                settings.update(json.load(f))
    except Exception as e:
        print(f"Error loading settings: {e}")

    include_violation = settings.get("include_violated_content", True)
    event_total = settings.get("event_tweets_count", 2500)
    daily_total = settings.get("daily_tweets_count", 1000)
    location = settings.get("violated_content_location", "النسيم")

    if base_time is None:
        # Yesterday at 14:00
        now = datetime.now()
        base_time = datetime(now.year, now.month, now.day, 14, 0, 0) - timedelta(days=1)
    
    tweets = []
    
    # ========== VIOLATED DATA GENERATION (Phases 0-3) ==========
    if include_violation:
        # Phase 0: Source Tweet
        source_time = base_time + timedelta(minutes=15)  # 14:15
        source_tweet = create_tweet(
            text="شوفوا وش صار اليوم عند المدرسة 😂🔥 المقطع كامل",
            created_at=source_time,
            author_name="فهد | لا للمدرسة",
            author_username="@fahad_ghost_99",
            is_source=True,
            has_video=True,
            reliability_score=0.25
        )
        source_conversation_id = source_tweet["id"]
        tweets.append(source_tweet)
        
        # Calculate phase counts based on event_total
        # Adjust percentages approximately: 5% early, 80% viral, 15% tail
        early_count = int(event_total * 0.05)
        viral_count = int(event_total * 0.80)
        tail_count = int(event_total * 0.15)
        
        # Phase 1: Early Adopters
        for i in range(early_count):
            minutes_offset = max(20, min(115, gaussian_random(60, 20)))
            tweet_time = base_time + timedelta(minutes=minutes_offset)
            
            if random.random() < 0.6:
                text = random.choice(REPLIES_TO_SOURCE)
                tweet = create_tweet(
                    text=text,
                    created_at=tweet_time,
                    author_name=generate_display_name(),
                    author_username=generate_username(),
                    reply_to=source_tweet["author_id"],
                    conversation_id=source_conversation_id
                )
            else:
                template = random.choice(CROWD_TEMPLATES_WITH_KEYWORDS)
                text = template.format(location=location)
                tweet = create_tweet(
                    text=text,
                    created_at=tweet_time,
                    author_name=generate_display_name(),
                    author_username=generate_username()
                )
            tweets.append(tweet)
        
        # Phase 2: Viral Explosion
        for i in range(viral_count):
            minutes_offset = 120 + log_normal_random(2.5, 0.7) * 30
            minutes_offset = max(120, min(360, minutes_offset))
            tweet_time = base_time + timedelta(minutes=minutes_offset)
            
            if random.random() < 0.70:
                template = random.choice(CROWD_TEMPLATES_WITH_KEYWORDS)
                text = template.format(location=location)
                if random.random() < 0.3:
                    text += f" #مضاربة_{location}"
            else:
                text = random.choice(CROWD_TEMPLATES_NOISE)
                if random.random() < 0.5:
                    text += f" #ترند_الرياض"
            
            tweet = create_tweet(
                text=text,
                created_at=tweet_time,
                author_name=generate_display_name(),
                author_username=generate_username()
            )
            tweets.append(tweet)
            
        # Phase 3: Tail
        for i in range(tail_count):
            minutes_offset = 360 + random.expovariate(0.01)
            minutes_offset = min(minutes_offset, 1440)
            tweet_time = base_time + timedelta(minutes=minutes_offset)
            
            if random.random() < 0.5:
                template = random.choice(CROWD_TEMPLATES_WITH_KEYWORDS)
                text = template.format(location=location)
            else:
                text = random.choice(CROWD_TEMPLATES_NOISE)
                
            tweet = create_tweet(
                text=text,
                created_at=tweet_time,
                author_name=generate_display_name(),
                author_username=generate_username()
            )
            tweets.append(tweet)

    # ========== PHASE 4: Daily Content (Throughout the day) ==========
    for i in range(daily_total):
        minutes_offset = random.uniform(0, 1440)
        tweet_time = base_time + timedelta(minutes=minutes_offset)
        
        text = random.choice(DAILY_CONTENT_TEMPLATES)
        has_image = random.random() < 0.15
        
        tweet = create_tweet(
            text=text,
            created_at=tweet_time,
            author_name=generate_display_name(),
            author_username=generate_username()
        )
        
        if has_image:
            tweet["media"] = [{
                "type": "photo",
                "media_key": f"img_{uuid.uuid4().hex[:8]}",
                "url": "https://picsum.photos/600/400"
            }]
        
        tweets.append(tweet)
    
    # Sort by timestamp
    tweets.sort(key=lambda t: t["created_at"])
    
    return tweets


def get_volume_by_hour(tweets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Calculate tweet volume per hour for charting."""
    volume = {}
    
    for tweet in tweets:
        dt = datetime.fromisoformat(tweet["created_at"].replace("Z", ""))
        hour = dt.hour
        volume[hour] = volume.get(hour, 0) + 1
    
    return [{"hour": h, "count": volume.get(h, 0)} for h in range(24)]


if __name__ == "__main__":
    # Test data generation
    tweets = generate_synthetic_dataset()
    print(f"Generated {len(tweets)} tweets")
    
    # Find source
    source = next(t for t in tweets if t.get("is_source"))
    print(f"Source tweet at: {source['created_at']}")
    print(f"Source text: {source['text']}")
    
    # Volume distribution
    volume = get_volume_by_hour(tweets)
    print("\nVolume by hour:")
    for v in volume:
        bar = "█" * (v["count"] // 20)
        print(f"  {v['hour']:02d}:00 | {bar} ({v['count']})")
