from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import re


def get_driver():

    options = webdriver.ChromeOptions()

    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    options.add_argument(
        "--user-agent=Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    # Chromium installed by packages.txt
    options.binary_location = "/usr/bin/chromium"

    driver = webdriver.Chrome(
        options=options
    )

    return driver


def scrape_with_selenium(url):

    driver = get_driver()
    texts = []

    try:

        driver.get(url)

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (By.TAG_NAME, "body")
            )
        )

        time.sleep(3)

        # Scroll to trigger lazy-loaded content
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight / 2);"
        )

        time.sleep(1)

        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);"
        )

        time.sleep(1)

        soup = BeautifulSoup(
            driver.page_source,
            "html.parser"
        )

        # Remove unnecessary elements
        for tag in soup(
            ["script", "style", "meta", "link", "noscript"]
        ):
            tag.decompose()

        def is_useful_text(text):

            if not text:
                return False

            text_lower = text.lower()

            # Ignore mostly numeric content
            if re.match(
                r'^[\d\s\.,₹%\+\-x]+$',
                text
            ):
                return False

            # Ignore keyboard shortcuts
            if "shift+" in text_lower or "alt+" in text_lower:
                return False

            # Ignore very short text
            if len(text.split()) < 3:
                return False

            boilerplate = [
                "sign in",
                "back to top",
                "skip to",
                "add to cart",
                "add to wish",
                "returns & orders",
                "terms of use",
                "privacy notice",
                "conditions of use",
                "loading",
                "sorry, there was",
                "please try again",
                "please select",
                "select the department",
                "previous slide",
                "next slide",
                "previous page",
                "next page",
                "start over",
                "read more",
                "read less",
                "see more",
                "see all",
                "click to",
                "double tap",
                "keyboard shortcut",
                "stream type",
                "playback rate",
                "current time",
                "remaining time",
                "captions off",
                "descriptions off",
                "audio track",
                "fullscreen",
                "write a product review",
                "share your thoughts",
                "report an issue",
                "fields with an asterisk",
                "filtering customer reviews"
            ]

            if any(
                phrase in text_lower
                for phrase in boilerplate
            ):
                return False

            words = text.split()

            num_count = sum(
                1
                for word in words
                if re.match(
                    r'^[\d\.,₹%\-\+]+$',
                    word
                )
            )

            if (
                len(words) > 0
                and num_count / len(words) > 0.4
            ):
                return False

            return True

        # Extract rendered text
        for tag in soup.find_all(
            [
                "span",
                "div",
                "p",
                "button",
                "a",
                "h1",
                "h2",
                "h3",
                "label"
            ]
        ):

            text = tag.get_text(
                " ",
                strip=True
            )

            if (
                3 < len(text) < 300
                and is_useful_text(text)
            ):
                texts.append(text)

        # Remove duplicates
        texts = list(set(texts))

    finally:

        driver.quit()

    return texts