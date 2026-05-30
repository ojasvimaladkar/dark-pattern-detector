# 🕵️ Dark Pattern Detector

A machine learning system that detects manipulative UI text patterns on e-commerce websites.

**[Live Demo →](https://dark-pattern-detector-b5utmyakz9ae9snmygzew2.streamlit.app/)**

## Problem
E-commerce platforms use psychological manipulation tactics — fake urgency, artificial scarcity, confirm shaming — to pressure users into purchases. These "dark patterns" are increasingly regulated under India's DPDP Act and GDPR globally, yet no automated detection tool exists for Indian consumers.

## What it does
- Scrapes any e-commerce URL using Selenium (full JavaScript rendering) and extracts UI text
- Classifies each text element as dark pattern or legitimate using a LinearSVC classifier
- Returns confidence scores, pattern categories, and detection rate
- Works on Amazon.in, Flipkart, and any e-commerce page

## Results

| Metric | Score |
|--------|-------|
| Accuracy | 93% |
| ROC-AUC | 0.973 |
| Cross-validated AUC (5-fold) | 0.987 ± 0.002 |
| Category Classification Accuracy | 94% |
| Models Compared | 4 (Logistic Regression, Random Forest, Gradient Boosting, LinearSVC) |
| Confidence Threshold | 95% (tuned to minimize false positives) |
| False Negatives | 9 / 236 |

## Key Findings from EDA
- Dark pattern text is significantly shorter than normal text (under 9 words on average)
- Confirm shaming phrases dominate trigram analysis ("no thanks i don't want")
- Scarcity patterns have the longest average text length of all categories
- Social proof patterns most frequently use location-based language ("united states purchased")
- Model correctly identifies 7 dark pattern categories with 94% accuracy

## Tech Stack

| Layer | Tool |
|-------|------|
| Scraping | Selenium + BeautifulSoup4 (JavaScript rendering) |
| NLP | TF-IDF Vectorizer (5000 features, unigrams + bigrams) |
| Classification | LinearSVC with Platt Scaling (best of 4 models compared) |
| Category Model | Logistic Regression (7 dark pattern categories) |
| App | Streamlit |
| Deployment | Streamlit Cloud |

## Dark Pattern Categories Detected
- **Urgency** — fake countdown timers, limited time deals
- **Scarcity** — low stock warnings, "only X left"
- **Social Proof** — "X people bought this", activity notifications
- **Misdirection** — misleading interface elements
- **Confirm Shaming** — guilt-based opt-out language
- **Obstruction** — making cancellation difficult
- **Forced Continuity** — auto-renewal, hidden subscriptions

## Project Structure

    dark-pattern-detector/
    ├── data/
    ├── notebooks/
    │   ├── 01_eda.ipynb
    │   └── 02_modelling.ipynb
    ├── models/
    │   ├── best_model.pkl
    │   ├── category_model.pkl
    │   └── tfidf_vectorizer.pkl
    ├── app/
    │   └── app.py
    ├── scraper.py
    ├── selenium_scraper.py
    ├── requirements.txt
    └── README.md

## Limitations
- Negative customer reviews occasionally flagged as Social Proof due to similar phrasing in training data
- Limited Hinglish coverage — model trained primarily on English text
- Forced Action and Sneaking categories underrepresented in training data (4 and 12 samples respectively)

## Future Work
- Multilingual support for Hinglish dark patterns
- Chrome extension for real-time detection on any page
- Fine-tuned DistilBERT for improved accuracy
- Expanded dataset with manually labelled Indian e-commerce samples