# 🕵️ Dark Pattern Detector

A machine learning system that detects manipulative UI text patterns on e-commerce websites.

**[Live Demo →](https://dark-pattern-detector-b5utmyakz9ae9snmygzew2.streamlit.app/)**

## Problem
E-commerce platforms use psychological manipulation tactics — fake urgency, artificial scarcity, confirm shaming — to pressure users into purchases. These "dark patterns" are increasingly regulated under India's DPDP Act and GDPR globally, yet no automated detection tool exists for Indian consumers.

## What it does
- Scrapes any e-commerce URL and extracts UI text
- Classifies each text element as dark pattern or legitimate
- Returns confidence scores and pattern categories
- Works on Amazon, Flipkart, Myntra and any static page

## Results
| Metric | Score |
|--------|-------|
| Accuracy | 93% |
| ROC-AUC | 0.97 |
| False Negatives | 9 / 236 |
| Training samples | 1884 |

## Key Findings from EDA
- Dark pattern text is significantly shorter than normal text (under 9 words on average)
- "Confirm shaming" phrases dominate trigram analysis ("no thanks i don't want")
- Scarcity patterns have the longest average text length
- Social proof patterns most frequently use location-based language ("united states purchased")

## Tech Stack
- **Scraping** — requests, BeautifulSoup4
- **NLP** — TF-IDF Vectorizer (5000 features, bigrams)
- **Model** — Logistic Regression (sklearn)
- **App** — Streamlit
- **Deployment** — Streamlit Cloud

## Limitations
- Dynamic JavaScript-rendered content (countdown timers, live stock counts) not captured by static scraping
- Model trained primarily on English text, limited Hinglish coverage
- Small representation of Forced Action and Sneaking categories in training data

## Project Structure
​```
dark-pattern-detector/
├── data/
├── notebooks/
│   ├── 01_eda.ipynb
│   └── 02_modelling.ipynb
├── models/
├── app/
│   └── app.py
├── scraper.py
└── requirements.txt
​```

## Future Work
- Selenium-based scraping for JavaScript-rendered content
- Multilingual support for Hinglish dark patterns
- Chrome extension for real-time detection
- Fine-tuned DistilBERT for higher accuracy