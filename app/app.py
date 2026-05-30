import streamlit as st
import joblib
import re
import requests
from bs4 import BeautifulSoup

model = joblib.load('models/best_model.pkl')
vectorizer = joblib.load('models/tfidf_vectorizer.pkl')
category_model = joblib.load('models/category_model.pkl')

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^a-z0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def scrape_texts(url):
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    import time

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36")

    texts = []
    driver = None

    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(3)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        for tag in soup(["script", "style", "meta", "link"]):
            tag.decompose()
        for tag in soup.find_all(["span", "div", "p", "button", "a", "h1", "h2", "h3"]):
            text = tag.get_text(strip=True)
            if 3 < len(text) < 200:
                texts.append(text)
        texts = list(set(texts))

    except Exception as e:
        st.error(f"Scraping error: {e}")
    finally:
        if driver:
            driver.quit()

    return texts

def predict(texts):
    cleaned = [clean_text(t) for t in texts]
    vectors = vectorizer.transform(cleaned)
    predictions = model.predict(vectors)
    probabilities = model.predict_proba(vectors)[:, 1]
    
    categories = []
    for i, pred in enumerate(predictions):
        if pred == 1:
            cat = category_model.predict(vectors[i])[0]
        else:
            cat = None
        categories.append(cat)
    
    return predictions, probabilities, categories

# ---- UI ----
st.set_page_config(page_title="Dark Pattern Detector", page_icon="🕵️", layout="wide")

st.title("🕵️ Dark Pattern Detector")
st.markdown("Detects manipulative UI text on e-commerce websites using Machine Learning.")

tab1, tab2 = st.tabs(["🔗 Scan a URL", "✍️ Check Custom Text"])

with tab1:
    st.subheader("Paste any e-commerce URL")
    url = st.text_input("URL", placeholder="https://www.amazon.in/dp/...")
    
    if st.button("Scan Page", type="primary"):
        if url:
            with st.spinner("Scraping page..."):
                texts = scrape_texts(url)
            
            if not texts:
                st.error("Couldn't scrape this page. Try a different URL.")
            else:
                preds, probs, cats = predict(texts)                
                noise_phrases = [
                    'captions off', 'descriptions off', 'remaining time', 'current time',
                    'about this item', 'this item:', 'bank offer', '1 offer', 'save 2%',
                    'save 5%', '10 days returnable', 'your recently viewed',
                    'get gst invoice', 'partner offers', 'purchase protection',
                    'to see our price', 'total price', 'add both to cart'
                ]

                dark_indices = [
                    i for i, p in enumerate(preds)
                    if p == 1
                    and probs[i] > 0.95
                    and not any(noise.lower() in texts[i].lower() for noise in noise_phrases)
                ]
                st.metric("Total text elements scraped", len(texts))
                st.metric("Dark patterns found", len(dark_indices))
                st.metric("Detection rate", f"{len(dark_indices)/len(texts)*100:.1f}%")
                
                if dark_indices:
                    st.subheader("🚨 Detected Dark Patterns")
                    for i in dark_indices:
                        confidence = probs[i] * 100
                        st.error(f"**{texts[i]}** — {cats[i]} — Confidence: {confidence:.1f}%")                
                else:
                    st.success("No dark patterns detected on this page.")
        else:
            st.warning("Please enter a URL.")

with tab2:
    st.subheader("Paste any UI text to check")
    custom_text = st.text_area("Text", placeholder="Only 2 left in stock! Order now!")
    
    if st.button("Check Text", type="primary"):
        if custom_text:
            preds, probs, cats = predict([custom_text])
            confidence = probs[0] * 100
            
            if preds[0] == 1:
                st.error(f"🚨 Dark Pattern Detected — **{cats[0]}** — Confidence: {confidence:.1f}%")
            else:
                st.success(f"✅ Not a Dark Pattern — Confidence: {100-confidence:.1f}%")
        else:
            st.warning("Please enter some text.")