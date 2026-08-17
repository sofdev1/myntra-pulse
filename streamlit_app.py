"""
streamlit_app.py
-----------------
Streamlit web interface for the Myntra Review Scrapper (alternative
to the Flask app in app.py).

Run with:
    streamlit run streamlit_app.py
Then open:
    http://localhost:8501
"""

import pandas as pd
import streamlit as st

from scraper import scrape_reviews

st.set_page_config(page_title="Myntra Review Scrapper", page_icon="🛍️", layout="wide")

st.title("🛍️ Myntra Review Scrapper")
st.markdown(
    "Extract and analyze customer reviews and ratings from Myntra product pages. "
    "Enter a product URL below to get started."
)

with st.form("scrape_form"):
    product_url = st.text_input(
        "Myntra Product URL",
        placeholder="https://www.myntra.com/tshirts/roadster/.../123456/buy",
    )
    submitted = st.form_submit_button("Scrape Reviews")

if submitted:
    if not product_url.strip():
        st.error("Please enter a Myntra product URL.")
    else:
        with st.spinner("Fetching and parsing reviews..."):
            try:
                df = scrape_reviews(product_url.strip())
            except ValueError as exc:
                st.error(str(exc))
                df = pd.DataFrame()
            except Exception as exc:  # pragma: no cover - defensive
                st.error(f"Something went wrong while scraping: {exc}")
                df = pd.DataFrame()

        if not df.empty:
            st.session_state["reviews_df"] = df

if "reviews_df" in st.session_state:
    df = st.session_state["reviews_df"]

    st.success(f"Found {len(df)} reviews.")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Reviews", len(df))
    if df["rating"].notna().any():
        col2.metric("Average Rating", f"{df['rating'].mean():.2f} ★")
    else:
        col2.metric("Average Rating", "N/A")
    col3.metric(
        "Data Source", df["source"].iloc[0] if "source" in df.columns else "unknown"
    )

    st.subheader("Rating Distribution")
    if df["rating"].notna().any():
        st.bar_chart(df["rating"].value_counts().sort_index())

    st.subheader("Reviews")
    st.dataframe(
        df[["reviewer_name", "rating", "review_date", "review_text"]],
        use_container_width=True,
    )

    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download CSV",
        data=csv_bytes,
        file_name="myntra_reviews.csv",
        mime="text/csv",
    )
else:
    st.info("Enter a product URL above and click **Scrape Reviews** to begin.")

st.markdown("---")
st.caption(
    "Note: Live scraping depends on Myntra's current page structure and may fall back "
    "to demo data if the site blocks automated requests. See README.md for details."
)
