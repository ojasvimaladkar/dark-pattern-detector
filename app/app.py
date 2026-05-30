import streamlit as st
import joblib
import re
import requests
from bs4 import BeautifulSoup

model = joblib.load('models/logistic_regression.pkl')
vectorizer = joblib.load('models/tfidf_vectorizer.pkl')

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^a-z0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def scrape_texts(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        for tag in soup(["script", "style", "meta", "link"]):
            tag.decompose()
        texts = []
        for tag in soup.find_all(["span", "div", "p", "button", "a", "h1", "h2", "h3"]):
            text = tag.get_text(strip=True)
            if 3 < len(text) < 200:
                texts.append(text)
        return list(set(texts))
    except Exception as e:
        return []

def predict(texts):
    cleaned = [clean_text(t) for t in texts]
    vectors = vectorizer.transform(cleaned)
    predictions = model.predict(vectors)
    probabilities = model.predict_proba(vectors)[:, 1]
    return predictions, probabilities

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
                preds, probs = predict(texts)
                dark_indices = [i for i, p in enumerate(preds) if p == 1]
                
                st.metric("Total text elements scraped", len(texts))
                st.metric("Dark patterns found", len(dark_indices))
                st.metric("Detection rate", f"{len(dark_indices)/len(texts)*100:.1f}%")
                
                if dark_indices:
                    st.subheader("🚨 Detected Dark Patterns")
                    for i in dark_indices:
                        confidence = probs[i] * 100
                        st.error(f"**{texts[i]}** — Confidence: {confidence:.1f}%")
                else:
                    st.success("No dark patterns detected on this page.")
        else:
            st.warning("Please enter a URL.")

with tab2:
    st.subheader("Paste any UI text to check")
    custom_text = st.text_area("Text", placeholder="Only 2 left in stock! Order now!")
    
    if st.button("Check Text", type="primary"):
        if custom_text:
            preds, probs = predict([custom_text])
            confidence = probs[0] * 100
            
            if preds[0] == 1:
                st.error(f"🚨 Dark Pattern Detected — Confidence: {confidence:.1f}%")
            else:
                st.success(f"✅ Not a Dark Pattern — Confidence: {100-confidence:.1f}%")
        else:
            st.warning("Please enter some text.")