"""
scraper.py
-----------
Core scraping logic for the Myntra Review Scrapper project.

Given a Myntra product URL, this module fetches the page, parses out
product reviews / ratings using BeautifulSoup, cleans the extracted
text, and returns a structured pandas DataFrame.

Note on real-world usage:
Myntra (like most modern e-commerce sites) renders a large portion of
its review content client-side via JavaScript and internal JSON APIs,
and it actively blocks simple scripted requests. This module is built
to:
  1. Try a direct HTML request + BeautifulSoup parse first (works for
     any static/server-rendered content or cached pages).
  2. Fall back to a mock/demo dataset generator when live scraping is
     blocked or returns no reviews, so the rest of the pipeline
     (cleaning -> storage -> UI -> download) can still be demoed and
     tested end-to-end without a live network dependency.

For production use against the real site, you would typically extend
`fetch_reviews_live` to call Myntra's internal review API endpoints
(inspect via browser dev tools -> Network tab) or use a headless
browser (Selenium / Playwright) to render JS before parsing.
"""

import re
import time
import random
import logging
from datetime import datetime, timedelta

import requests
import pandas as pd
from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

REQUEST_TIMEOUT = 10  # seconds


class ScraperError(Exception):
    """Raised when the scraper cannot retrieve or parse a page."""


def is_valid_myntra_url(url: str) -> bool:
    """Basic validation that the given URL looks like a Myntra product URL."""
    pattern = r"^https?://(www\.)?myntra\.com/.+"
    return bool(re.match(pattern, url.strip(), re.IGNORECASE))


def fetch_page_html(url: str) -> str:
    """Fetch raw HTML for a product URL."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.text
    except requests.RequestException as exc:
        logger.warning("Live fetch failed (%s). Will fall back to demo data.", exc)
        raise ScraperError(str(exc)) from exc


def parse_reviews_from_html(html: str) -> list:
    """
    Parse review blocks out of raw HTML using BeautifulSoup.

    Myntra's review markup changes frequently and much of it is loaded
    via JS, so this parser is intentionally defensive: it looks for a
    handful of common class-name patterns and simply returns an empty
    list if nothing matches, letting the caller fall back to demo data.
    """
    soup = BeautifulSoup(html, "html.parser")
    reviews = []

    candidate_selectors = [
        {"class": re.compile(r"user-review", re.I)},
        {"class": re.compile(r"review-comment", re.I)},
        {"class": re.compile(r"review-card", re.I)},
    ]

    blocks = []
    for selector in candidate_selectors:
        blocks = soup.find_all(attrs=selector)
        if blocks:
            break

    for block in blocks:
        text = clean_text(block.get_text(separator=" "))
        rating_tag = block.find(attrs={"class": re.compile(r"rating", re.I)})
        rating = extract_rating(rating_tag.get_text()) if rating_tag else None
        if text:
            reviews.append(
                {
                    "review_text": text,
                    "rating": rating,
                    "review_date": None,
                    "reviewer_name": None,
                }
            )

    return reviews


def clean_text(text: str) -> str:
    """Remove excess whitespace and non-printable characters from scraped text."""
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text)
    text = text.strip()
    return text


def extract_rating(text: str):
    """Pull a numeric rating (e.g. 4.5) out of a string, if present."""
    match = re.search(r"(\d(?:\.\d)?)", text)
    return float(match.group(1)) if match else None


def generate_demo_reviews(product_url: str, n: int = 25) -> list:
    """
    Generate a realistic-looking demo review dataset.

    Used as a fallback so the full pipeline (fetch -> clean -> store ->
    display -> download) can be exercised end-to-end even when the live
    site blocks scripted requests or has changed its markup.
    """
    sample_comments = [
        "Great quality fabric, fits perfectly and looks exactly like the pictures.",
        "Good product but delivery took longer than expected.",
        "Color is slightly different from what was shown online.",
        "Excellent value for money, will definitely order again.",
        "Size runs a bit small, order one size up.",
        "Loved it! Super comfortable for daily wear.",
        "Average quality, expected better stitching for the price.",
        "Fast delivery and well packaged. Very satisfied.",
        "Not as described, material feels cheap.",
        "Perfect fit and great customer service when I had a query.",
    ]
    names = [
        "Aarav",
        "Priya",
        "Rohan",
        "Sneha",
        "Karan",
        "Isha",
        "Vikram",
        "Neha",
        "Aditya",
        "Pooja",
    ]

    random.seed(hash(product_url) % (10**6))
    reviews = []
    base_date = datetime.now()
    for i in range(n):
        reviews.append(
            {
                "review_text": random.choice(sample_comments),
                "rating": round(random.uniform(2.5, 5.0), 1),
                "review_date": (
                    base_date - timedelta(days=random.randint(0, 180))
                ).strftime("%Y-%m-%d"),
                "reviewer_name": random.choice(names),
            }
        )
    return reviews


def scrape_reviews(product_url: str, use_demo_fallback: bool = True) -> pd.DataFrame:
    """
    Main entry point: scrape reviews for a given Myntra product URL and
    return them as a cleaned pandas DataFrame.

    Parameters
    ----------
    product_url : str
        Full URL to a Myntra product page.
    use_demo_fallback : bool
        If True (default), fall back to generated demo data when live
        scraping fails or returns zero reviews. Set False to force a
        live-only result (may return an empty DataFrame).

    Returns
    -------
    pandas.DataFrame with columns:
        review_text, rating, review_date, reviewer_name, product_url, scraped_at
    """
    if not is_valid_myntra_url(product_url):
        raise ValueError(
            "Please provide a valid Myntra product URL (https://www.myntra.com/...)"
        )

    reviews = []
    source = "live"
    try:
        html = fetch_page_html(product_url)
        reviews = parse_reviews_from_html(html)
    except ScraperError:
        reviews = []

    if not reviews and use_demo_fallback:
        logger.info("No live reviews found — generating demo dataset instead.")
        reviews = generate_demo_reviews(product_url)
        source = "demo"

    df = pd.DataFrame(reviews)
    if df.empty:
        return df

    df["review_text"] = df["review_text"].apply(clean_text)
    df["product_url"] = product_url
    df["scraped_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df["source"] = source
    df.drop_duplicates(subset=["review_text", "reviewer_name"], inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


def save_reviews_to_csv(df: pd.DataFrame, filepath: str) -> str:
    """Persist a reviews DataFrame to CSV and return the filepath."""
    df.to_csv(filepath, index=False)
    logger.info("Saved %d reviews to %s", len(df), filepath)
    return filepath


if __name__ == "__main__":
    # Simple manual test
    test_url = "https://www.myntra.com/tshirts/roadster/sample-product/123456/buy"
    result_df = scrape_reviews(test_url)
    print(result_df.head())
    save_reviews_to_csv(result_df, "data/sample_reviews.csv")
