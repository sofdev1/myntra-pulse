"""
app.py
------
Flask web interface for the Myntra Review Scrapper.

Run with:
    python app.py
Then open:
    http://localhost:5000

For production, serve with gunicorn, e.g.:
    gunicorn app:app --bind 0.0.0.0:5000
"""

import os
import logging

from flask import Flask, render_template, request, send_file, flash, redirect, url_for

from scraper import scrape_reviews

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY", "dev-secret-key-change-in-production"
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)
LATEST_CSV_PATH = os.path.join(DATA_DIR, "latest_reviews.csv")


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/scrape", methods=["POST"])
def scrape():
    product_url = request.form.get("product_url", "").strip()

    if not product_url:
        flash("Please enter a Myntra product URL.")
        return redirect(url_for("index"))

    try:
        df = scrape_reviews(product_url)
    except ValueError as exc:
        flash(str(exc))
        return redirect(url_for("index"))
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Unexpected scraping error")
        flash(f"Something went wrong while scraping: {exc}")
        return redirect(url_for("index"))

    if df.empty:
        flash("No reviews were found for this product.")
        return redirect(url_for("index"))

    df.to_csv(LATEST_CSV_PATH, index=False)

    summary = {
        "product_url": product_url,
        "review_count": len(df),
        "average_rating": (
            round(df["rating"].mean(), 2) if df["rating"].notna().any() else None
        ),
        "source": df["source"].iloc[0] if "source" in df.columns else "unknown",
    }

    reviews = df.to_dict(orient="records")
    return render_template("results.html", reviews=reviews, summary=summary)


@app.route("/download")
def download():
    if not os.path.exists(LATEST_CSV_PATH):
        flash("No scraped data available to download yet.")
        return redirect(url_for("index"))
    return send_file(
        LATEST_CSV_PATH, as_attachment=True, download_name="myntra_reviews.csv"
    )


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
