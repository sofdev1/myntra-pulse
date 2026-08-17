"""
tests/test_scraper.py
----------------------
Basic unit tests for the scraper module. Run with:
    pytest
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
import pytest

from scraper import (
    is_valid_myntra_url,
    clean_text,
    extract_rating,
    generate_demo_reviews,
    scrape_reviews,
)


def test_is_valid_myntra_url_accepts_valid_urls():
    assert is_valid_myntra_url("https://www.myntra.com/tshirts/roadster/x/123/buy")
    assert is_valid_myntra_url("http://myntra.com/shoes/nike/y/456/buy")


def test_is_valid_myntra_url_rejects_invalid_urls():
    assert not is_valid_myntra_url("https://www.amazon.com/product/123")
    assert not is_valid_myntra_url("not a url")
    assert not is_valid_myntra_url("")


def test_clean_text_collapses_whitespace():
    assert clean_text("  hello   world  \n") == "hello world"
    assert clean_text("") == ""
    assert clean_text(None) == ""


def test_extract_rating_finds_numeric_value():
    assert extract_rating("4.5 out of 5") == 4.5
    assert extract_rating("Rated 3") == 3.0
    assert extract_rating("no rating here") is None


def test_generate_demo_reviews_returns_expected_count():
    reviews = generate_demo_reviews("https://www.myntra.com/x/y/1/buy", n=10)
    assert len(reviews) == 10
    for r in reviews:
        assert "review_text" in r
        assert "rating" in r
        assert 1.0 <= r["rating"] <= 5.0


def test_scrape_reviews_rejects_invalid_url():
    with pytest.raises(ValueError):
        scrape_reviews("https://www.google.com")


def test_scrape_reviews_returns_dataframe_with_expected_columns():
    df = scrape_reviews("https://www.myntra.com/tshirts/roadster/sample/123/buy")
    assert isinstance(df, pd.DataFrame)
    expected_cols = {
        "review_text",
        "rating",
        "review_date",
        "reviewer_name",
        "product_url",
        "scraped_at",
        "source",
    }
    assert expected_cols.issubset(set(df.columns))
    assert len(df) > 0
