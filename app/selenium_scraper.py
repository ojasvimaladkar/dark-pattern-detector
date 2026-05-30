from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time
import re


def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # run without opening a visible window
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    return driver


def scrape_with_selenium(url):
    driver = get_driver()
    texts = []

    try:
        driver.get(url)

        # wait for page to fully load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # extra wait for dynamic content to render
        time.sleep(3)

        # scroll down to trigger lazy loaded content
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight/2);"
        )
        time.sleep(1)

        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);"
        )
        time.sleep(1)

        # now get the fully rendered HTML
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        for tag in soup(["script", "style", "meta", "link"]):
            tag.decompose()

        import re

        def is_useful_text(text):
            if re.match(r'^[\d\s\.,₹%\+\-x]+$', text):
                return False
            if 'shift+' in text.lower() or 'alt+' in text.lower():
                return False
            if len(text.split()) < 3:
                return False
            boilerplate = [
                'sign in', 'back to top', 'skip to', 'add to cart', 'add to wish',
                'returns & orders', 'terms of use', 'privacy notice', 'conditions of use',
                'loading', 'sorry, there was', 'please try again', 'please select',
                'select the department', 'previous slide', 'next slide', 'previous page',
                'next page', 'start over', 'read more', 'read less', 'see more',
                'see all', 'click to', 'double tap', 'keyboard shortcut',
                'stream type', 'playback rate', 'current time', 'remaining time',
                'captions off', 'descriptions off', 'audio track', 'fullscreen',
                'write a product review', 'share your thoughts', 'report an issue',
                'fields with an asterisk', 'filtering customer reviews'
            ]
            if any(b in text.lower() for b in boilerplate):
                return False
            # remove texts that are mostly numbers mixed with text
            words = text.split()
            num_count = sum(1 for w in words if re.match(r'^[\d\.,₹%\-\+]+$', w))
            if len(words) > 0 and num_count / len(words) > 0.4:
                return False
            return True

        for tag in soup.find_all(
            ["span", "div", "p", "button", "a", "h1", "h2", "h3", "label"]
        ):
            text = tag.get_text(strip=True)

            if 3 < len(text) < 300 and is_useful_text(text):
                texts.append(text)

        texts = list(set(texts))

    except Exception as e:
        print(f"Error: {e}")

    finally:
        driver.quit()  # always close browser

    return texts


if __name__ == "__main__":
    url = "https://www.amazon.in/Enflamo-Polycarbonate-Compatible-Designed-Protection/dp/B0C5VQQ5GF/"

    print("Scraping with Selenium...")
    texts = scrape_with_selenium(url)

    print(f"Total texts found: {len(texts)}")

    # check if we caught the dark patterns we saw manually
    targets = [
        "5 hrs",
        "bought in past month",
        "Amazon's Choice",
        "usually keep"
    ]

    print("\nChecking for known dark patterns:")

    for target in targets:
        found = any(target.lower() in t.lower() for t in texts)
        print(f"  '{target}': {'FOUND' if found else 'MISSED'}")

    # print all texts for inspection
    print("\nAll scraped texts:")

    for t in sorted(texts):
        print(f"  - {t.encode('ascii', 'ignore').decode()}")