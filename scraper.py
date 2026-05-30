import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (Chrome/120.0.0.0 Safari/537.36)"
}

DARK_PATTERN_TYPES = {
    "urgency": [
        "only left", "selling fast", "limited time", "deal ends", "expires in",
        "hurry", "last chance", "today only", "offer ends", "minutes left"
    ],
    "scarcity": [
        "only 1 left", "only 2 left", "only 3 left", "low stock", "almost gone",
        "few left", "limited stock", "in high demand", "selling out"
    ],
    "social_proof": [
        "people are viewing", "others are looking", "bought this today",
        "popular choice", "trending", "bestseller", "people bought"
    ],
    "confirm_shaming": [
        "no thanks i don't want", "no thanks i hate", "i don't want to save",
        "no i don't want deals", "i'll pay full price", "no thanks i prefer"
    ],
    "hidden_costs": [
        "convenience fee", "handling fee", "service fee", "packaging fee",
        "platform fee", "gst extra", "taxes not included"
    ],
    "forced_continuity": [
        "auto renew", "automatically renewed", "cancel anytime",
        "free trial then", "subscription starts", "recurring charge"
    ]
}

def classify_text(text):
    text_lower = text.lower()
    for pattern_type, keywords in DARK_PATTERN_TYPES.items():
        for keyword in keywords:
            if keyword in text_lower:
                return pattern_type, keyword
    return None, None

def scrape_page(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(["script", "style", "meta", "link"]):
            tag.decompose()

        texts = []
        for tag in soup.find_all(["span", "div", "p", "button", "a", "h1", "h2", "h3", "label"]):
            text = tag.get_text(strip=True)
            if 3 < len(text) < 200:  
                texts.append(text)

        return list(set(texts))  

    except Exception as e:
        print(f"Failed to scrape {url}: {e}")
        return []

def build_dataset(urls):
    records = []

    for url in urls:
        print(f"Scraping: {url}")
        texts = scrape_page(url)

        for text in texts:
            pattern_type, trigger_keyword = classify_text(text)
            records.append({
                "text": text,
                "pattern_type": pattern_type,
                "trigger_keyword": trigger_keyword,
                "is_dark_pattern": 1 if pattern_type else 0,
                "source_url": url,
                "platform": "amazon" if "amazon" in url else "flipkart" if "flipkart" in url else "other"
            })

        time.sleep(random.uniform(1, 2))  # be polite, don't get blocked

    return pd.DataFrame(records)


URLS = [
    "https://www.amazon.in/dp/B08N5WRWNW",
    "https://www.amazon.in/dp/B07HGGFQCD",
    "https://www.amazon.in/dp/B09G3HRMVB",
    "https://www.flipkart.com/apple-iphone-13/p/itmca361ec2a6b61",
    "https://www.flipkart.com/boAt-rockerz-450/p/itm6a9b1f0ee0772",
]

if __name__ == "__main__":
    df = build_dataset(URLS)
    df.to_csv("data/raw_scraped.csv", index=False)
    print(f"\nDone. {len(df)} text samples scraped.")
    print(f"Dark patterns found: {df['is_dark_pattern'].sum()}")
    print(df['pattern_type'].value_counts())