"""
NLP Engine - Crowd Echo Algorithm
Extracts semantic fingerprints from Arabic tweet datasets.
"""

from typing import List, Dict, Any, Set, Tuple
from collections import Counter
from datetime import datetime
import re

# Comprehensive Arabic stop words list
ARABIC_STOP_WORDS: Set[str] = {
    # Prepositions
    "في", "من", "على", "إلى", "الى", "عن", "مع", "بين", "حتى", "منذ",
    "خلال", "عند", "لدى", "ضد", "نحو", "فوق", "تحت", "أمام", "وراء",
    
    # Pronouns
    "أنا", "انا", "أنت", "انت", "أنتم", "انتم", "هو", "هي", "هم", "هن",
    "نحن", "انتي", "أنتي", "هذا", "هذه", "ذلك", "تلك", "هؤلاء", "أولئك",
    
    # Conjunctions
    "و", "أو", "او", "ثم", "لكن", "بل", "لأن", "لان", "إذا", "اذا",
    "لو", "كي", "حين", "عندما", "بينما", "كما", "مثل", "إن", "ان", "أن",
    
    # Articles & Particles
    "ال", "الـ", "لا", "لم", "لن", "ما", "قد", "سوف", "سـ", "كل",
    "بعض", "كثير", "قليل", "جدا", "جداً", "فقط", "أيضا", "ايضا",
    
    # Common verbs (conjugated)
    "كان", "كانت", "يكون", "تكون", "كانوا", "يكونون", "هناك",
    "صار", "أصبح", "اصبح", "بات", "ظل", "مازال",
    
    # Dialetical (Saudi/Gulf)
    "وش", "ايش", "ليش", "كيف", "متى", "وين", "منو", "شنو",
    "مو", "مب", "بس", "يعني", "طيب", "زين", "اوكي", "خلاص",
    "اللي", "اللى", "الي", "اله", "له", "لها", "لهم", "عليه", "عليها",
    "فيه", "فيها", "منه", "منها", "بعد", "قبل",
    
    # Common fillers
    "يا", "ياء", "آه", "اه", "والله", "وش", "هاه",
    
    # Twitter-specific
    "rt", "via", "cc", "dm",
    
    # Punctuation and emojis (will be handled separately)
}

# Regex pattern for Arabic text cleaning
ARABIC_PATTERN = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+')
HASHTAG_PATTERN = re.compile(r'#\w+')
MENTION_PATTERN = re.compile(r'@\w+')
URL_PATTERN = re.compile(r'https?://\S+')


def clean_text(text: str) -> str:
    """Remove URLs, mentions, and clean Arabic text."""
    text = URL_PATTERN.sub('', text)
    text = MENTION_PATTERN.sub('', text)
    # Keep hashtags for analysis but remove the # symbol later
    return text.strip()


def tokenize_arabic(text: str) -> List[str]:
    """
    Tokenize Arabic text by splitting on spaces and punctuation.
    Preserves Arabic characters only.
    """
    # Clean the text first
    cleaned = clean_text(text)
    
    # Split by whitespace and common Arabic punctuation
    tokens = re.split(r'[\s،.!؟:؛…\-_\(\)\[\]«»"\']+', cleaned)
    
    # Filter empty tokens and very short ones
    tokens = [t.strip() for t in tokens if t.strip() and len(t.strip()) > 1]
    
    return tokens


def remove_stop_words(tokens: List[str]) -> List[str]:
    """Remove Arabic stop words from token list."""
    return [t for t in tokens if t not in ARABIC_STOP_WORDS]


def extract_hashtags(text: str) -> List[str]:
    """Extract hashtags from text."""
    hashtags = HASHTAG_PATTERN.findall(text)
    return [h[1:] for h in hashtags]  # Remove # symbol


def calculate_ngram_frequency(
    tokens: List[str], 
    n: int = 1
) -> Dict[str, int]:
    """Calculate n-gram frequencies."""
    if n == 1:
        return dict(Counter(tokens))
    
    ngrams = []
    for i in range(len(tokens) - n + 1):
        ngram = " ".join(tokens[i:i+n])
        ngrams.append(ngram)
    
    return dict(Counter(ngrams))


def extract_semantic_fingerprint(
    dataset: List[Dict[str, Any]],
    report_time: datetime = None,
    top_k: int = 3
) -> Dict[str, Any]:
    """
    Extract semantic fingerprint from tweet dataset.
    
    Algorithm (Crowd Echo):
    1. Filter tweets after report time (if provided)
    2. Tokenize Arabic text
    3. Remove stop words
    4. Calculate unigram and bigram frequencies
    5. Return top keywords
    
    Args:
        dataset: List of tweet objects
        report_time: Only analyze tweets after this time
        top_k: Number of top keywords to return
    
    Returns:
        Dictionary containing:
        - top_keywords: List of most frequent meaningful words
        - unigram_freq: Full unigram frequency dict
        - bigram_freq: Full bigram frequency dict
        - total_tweets_analyzed: Count of processed tweets
        - hashtag_freq: Frequency of hashtags
    """
    
    # Step 1: Filter by time if report_time provided
    if report_time:
        filtered_tweets = [
            t for t in dataset 
            if datetime.fromisoformat(t["created_at"].replace("Z", "")) >= report_time
        ]
    else:
        filtered_tweets = dataset
    
    all_tokens = []
    all_hashtags = []
    
    # Step 2 & 3: Tokenize and collect
    for tweet in filtered_tweets:
        text = tweet.get("text", "")
        
        # Extract hashtags separately
        hashtags = extract_hashtags(text)
        all_hashtags.extend(hashtags)
        
        # Tokenize
        tokens = tokenize_arabic(text)
        
        # Remove stop words
        filtered_tokens = remove_stop_words(tokens)
        
        all_tokens.extend(filtered_tokens)
    
    # Step 4: Calculate frequencies
    unigram_freq = calculate_ngram_frequency(all_tokens, n=1)
    bigram_freq = calculate_ngram_frequency(all_tokens, n=2)
    hashtag_freq = dict(Counter(all_hashtags))
    
    # Step 5: Get top keywords (excluding very common generic words)
    # Sort by frequency
    sorted_unigrams = sorted(
        unigram_freq.items(), 
        key=lambda x: x[1], 
        reverse=True
    )
    
    # Filter out generic words that might slip through
    generic_words = {"الله", "الناس", "اليوم", "الحين", "شي", "اكثر", "كلام"}
    top_keywords = [
        word for word, count in sorted_unigrams 
        if word not in generic_words
    ][:top_k]
    
    # Also get top bigrams
    sorted_bigrams = sorted(
        bigram_freq.items(),
        key=lambda x: x[1],
        reverse=True
    )[:5]
    
    return {
        "top_keywords": top_keywords,
        "top_bigrams": [bg[0] for bg in sorted_bigrams],
        "unigram_freq": unigram_freq,
        "bigram_freq": bigram_freq,
        "hashtag_freq": hashtag_freq,
        "total_tweets_analyzed": len(filtered_tweets),
        "total_tokens": len(all_tokens)
    }


def find_tweets_with_keywords(
    dataset: List[Dict[str, Any]],
    keywords: List[str],
    start_time: datetime = None,
    end_time: datetime = None
) -> List[Dict[str, Any]]:
    """
    Find tweets containing any of the specified keywords within time range.
    """
    results = []
    
    for tweet in dataset:
        tweet_time = datetime.fromisoformat(tweet["created_at"].replace("Z", ""))
        
        # Time filter
        if start_time and tweet_time < start_time:
            continue
        if end_time and tweet_time > end_time:
            continue
        
        # Keyword filter
        text = tweet.get("text", "")
        if any(kw in text for kw in keywords):
            results.append(tweet)
    
    return results


def count_tweets_in_range(
    dataset: List[Dict[str, Any]],
    keywords: List[str],
    start_time: datetime,
    end_time: datetime
) -> int:
    """Count tweets with keywords in time range."""
    return len(find_tweets_with_keywords(dataset, keywords, start_time, end_time))


if __name__ == "__main__":
    # Test NLP engine
    from data_generator import generate_synthetic_dataset
    
    tweets = generate_synthetic_dataset()
    print(f"Generated {len(tweets)} tweets for NLP testing")
    
    # Extract fingerprint
    fingerprint = extract_semantic_fingerprint(tweets)
    
    print(f"\n📊 Semantic Fingerprint Analysis")
    print(f"   Tweets analyzed: {fingerprint['total_tweets_analyzed']}")
    print(f"   Total tokens: {fingerprint['total_tokens']}")
    print(f"\n   Top Keywords: {fingerprint['top_keywords']}")
    print(f"   Top Bigrams: {fingerprint['top_bigrams']}")
    print(f"\n   Top Hashtags:")
    for tag, count in sorted(fingerprint['hashtag_freq'].items(), key=lambda x: -x[1])[:5]:
        print(f"      #{tag}: {count}")
